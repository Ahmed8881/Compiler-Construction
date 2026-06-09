from __future__ import annotations
import sys
from typing import Iterator

TABLE_SIZE = 211


class Entry:

    def __init__(
        self,
        name: str,
        kind: str,
        type_: str,
        scope_level: int,
        line: int,
        next: Entry | None = None,
    ) -> None:
        self.name = str(name)
        self.kind = str(kind)
        self.type = str(type_)
        self.scope_level = int(scope_level)
        self.line = int(line)
        self.next = next
        self._order = 0

    def __repr__(self) -> str:
        return (
            f"Entry(name={self.name}, kind={self.kind}, type={self.type}, "
            f"scope={self.scope_level}, line={self.line})"
        )


class SymTable:

    def __init__(self, parent: SymTable | None = None, scope_level: int = 0) -> None:
        self.slots: list[Entry | None] = [None] * TABLE_SIZE
        self.scope_level = int(scope_level)
        self.parent = parent
        self._next_order = 0

    def _hash(self, name: str) -> int:
        h = 5381
        for char in name or "":
            h = ((h << 5) + h) + ord(char)
        return h % TABLE_SIZE

    def insert(self, name: str, kind: str, type_: str, line: int) -> Entry | None:
        if self.lookup_current(name) is not None:
            sys.stderr.write(f"ERROR line {line}: duplicate declaration '{name}'\n")
            return None

        index = self._hash(name)
        entry = Entry(name, kind, type_, self.scope_level, line, self.slots[index])
        entry._order = self._next_order
        self._next_order += 1
        self.slots[index] = entry
        return entry

    def lookup(self, name: str) -> Entry | None:
        index = self._hash(name)
        current: SymTable | None = self
        while current is not None:
            entry = current.slots[index]
            while entry is not None:
                if entry.name == name:
                    return entry
                entry = entry.next
            current = current.parent
        return None

    def lookup_current(self, name: str) -> Entry | None:
        index = self._hash(name)
        entry = self.slots[index]
        while entry is not None:
            if entry.name == name:
                return entry
            entry = entry.next
        return None

    def delete(self, name: str) -> bool:
        index = self._hash(name)
        previous: Entry | None = None
        entry = self.slots[index]
        while entry is not None:
            if entry.name == name:
                if previous is None:
                    self.slots[index] = entry.next
                else:
                    previous.next = entry.next
                return True
            previous = entry
            entry = entry.next
        return False

    def _iter_entries(self) -> Iterator[Entry]:
        for slot in self.slots:
            entry = slot
            while entry is not None:
                yield entry
                entry = entry.next

    def print_table(self) -> None:
        entries = sorted(
            self._iter_entries(),
            key=lambda entry: (entry.line, entry._order, entry.name, entry.kind),
        )

        widths = {
            "ID": 4,
            "Name": 12,
            "Kind": 12,
            "Type": 9,
            "Scope": 7,
            "Line": 6,
        }

        def border() -> str:
            return (
                "+"
                + "+".join("-" * widths[column] for column in ["ID", "Name", "Kind", "Type", "Scope", "Line"])
                + "+"
            )

        def row(values: list[str]) -> str:
            return (
                "|"
                + f" {values[0]:>{widths['ID'] - 1}} |"
                + f" {values[1]:<{widths['Name'] - 1}} |"
                + f" {values[2]:<{widths['Kind'] - 1}} |"
                + f" {values[3]:<{widths['Type'] - 1}} |"
                + f" {values[4]:^{widths['Scope'] - 1}} |"
                + f" {values[5]:^{widths['Line'] - 1}} |"
            )

        print(border())
        print(row(["ID", "Name", "Kind", "Type", "Scope", "Line"]))
        print(border())
        for index, entry in enumerate(entries, start=1):
            print(
                row(
                    [
                        str(index),
                        entry.name,
                        entry.kind,
                        entry.type,
                        str(entry.scope_level),
                        str(entry.line),
                    ]
                )
            )
        print(border())


def begin_scope(current: SymTable | None) -> SymTable:
    new_scope = SymTable(
        parent=current,
        scope_level=0 if current is None else current.scope_level + 1,
    )
    print(f"[Scope {new_scope.scope_level}] Enter")
    return new_scope


def end_scope(current: SymTable) -> SymTable | None:
    print(f"[Scope {current.scope_level}] Exit, dump:")
    current.print_table()
    return current.parent


def print_all_scopes(current: SymTable) -> None:
    scope = current
    while scope is not None:
        scope.print_table()
        scope = scope.parent
