"""Nested symbol table utilities for the lab submission."""

from __future__ import annotations

import sys
from typing import Iterator

BUCKET_COUNT = 211


class SymbolCell:
    """One chained record stored inside a hash bucket."""

    def __init__(
        self,
        label: str,
        category: str,
        data_type: str,
        level: int,
        lineno: int,
        chain: SymbolCell | None = None,
    ) -> None:
        self.label = str(label)
        self.category = str(category)
        self.data_type = str(data_type)
        self.level = int(level)
        self.lineno = int(lineno)
        self.chain = chain
        self.order = 0

    def __repr__(self) -> str:
        return (
            f"SymbolCell(label={self.label}, category={self.category}, "
            f"data_type={self.data_type}, level={self.level}, lineno={self.lineno})"
        )


class ScopeTable:
    """A single scope backed by a chained hash table."""

    def __init__(self, parent: ScopeTable | None = None, level: int = 0) -> None:
        self.buckets: list[SymbolCell | None] = [None] * BUCKET_COUNT
        self.level = int(level)
        self.parent = parent
        self._next_order = 0

    def _slot(self, label: str) -> int:
        h = 5381
        for char in label or "":
            h = ((h << 5) + h) + ord(char)
        return h % BUCKET_COUNT

    def insert(self, label: str, category: str, data_type: str, lineno: int) -> SymbolCell | None:
        if self.find_here(label) is not None:
            sys.stderr.write(f"ERROR line {lineno}: duplicate declaration '{label}'\n")
            return None

        index = self._slot(label)
        cell = SymbolCell(label, category, data_type, self.level, lineno, self.buckets[index])
        cell.order = self._next_order
        self._next_order += 1
        self.buckets[index] = cell
        return cell

    def find(self, label: str) -> SymbolCell | None:
        index = self._slot(label)
        current: ScopeTable | None = self
        while current is not None:
            node = current.buckets[index]
            while node is not None:
                if node.label == label:
                    return node
                node = node.chain
            current = current.parent
        return None

    def find_here(self, label: str) -> SymbolCell | None:
        index = self._slot(label)
        node = self.buckets[index]
        while node is not None:
            if node.label == label:
                return node
            node = node.chain
        return None

    def erase(self, label: str) -> bool:
        index = self._slot(label)
        prior: SymbolCell | None = None
        node = self.buckets[index]
        while node is not None:
            if node.label == label:
                if prior is None:
                    self.buckets[index] = node.chain
                else:
                    prior.chain = node.chain
                return True
            prior = node
            node = node.chain
        return False

    def _items(self) -> Iterator[SymbolCell]:
        for bucket in self.buckets:
            node = bucket
            while node is not None:
                yield node
                node = node.chain

    def render(self) -> None:
        rows = sorted(
            self._items(),
            key=lambda item: (item.lineno, item.order, item.label, item.category),
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
                + "+".join("-" * widths[col] for col in ["ID", "Name", "Kind", "Type", "Scope", "Line"])
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
        for number, entry in enumerate(rows, start=1):
            print(
                row(
                    [
                        str(number),
                        entry.label,
                        entry.category,
                        entry.data_type,
                        str(entry.level),
                        str(entry.lineno),
                    ]
                )
            )
        print(border())


def open_scope(previous: ScopeTable | None) -> ScopeTable:
    level = 0 if previous is None else previous.level + 1
    opened = ScopeTable(parent=previous, level=level)
    print(f"[Scope {opened.level}] Enter")
    return opened


def close_scope(current: ScopeTable) -> ScopeTable | None:
    print(f"[Scope {current.level}] Exit, dump:")
    current.render()
    return current.parent


def dump_all_scopes(current: ScopeTable) -> None:
    cursor = current
    while cursor is not None:
        cursor.render()
        cursor = cursor.parent
