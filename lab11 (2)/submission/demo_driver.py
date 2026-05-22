
from __future__ import annotations
import sys

from src.scope_table import ScopeTable, close_scope, open_scope


def report_error(text: str) -> None:
    sys.stderr.write(text + "\n")


def nested_scope_demo() -> None:
    root_scope = open_scope(None)
    root_scope.insert("mainProg", "function", "integer", lineno=1)
    root_scope.insert("input", "parameter", "integer", lineno=1)
    root_scope.insert("output", "parameter", "integer", lineno=1)
    root_scope.insert("x", "variable", "integer", lineno=2)
    root_scope.insert("y", "variable", "integer", lineno=3)

    child_scope = open_scope(root_scope)
    child_scope.insert("argA", "parameter", "integer", lineno=4)
    child_scope.insert("argB", "parameter", "integer", lineno=4)

    inner_scope = open_scope(child_scope)
    inner_scope.insert("z", "variable", "integer", lineno=6)

    match = inner_scope.find("x")
    if match is not None:
        print(f"[Scope 2] lookup x -> found at scope {match.level}")

    match = inner_scope.find("y")
    if match is not None:
        print(f"[Scope 2] lookup y -> found at scope {match.level}")

    inner_scope.insert("x", "variable", "integer", lineno=8)
    match = inner_scope.find("x")
    if match is not None:
        print(f"[Scope 2] lookup x -> found at scope {match.level} after shadowing")

    inner_scope = close_scope(inner_scope)
    child_scope = close_scope(child_scope)

    root_scope.insert("x", "variable", "integer", lineno=11)
    match = root_scope.find("a")
    if match is None:
        report_error("ERROR line 12: undeclared variable 'a'")

    root_scope = close_scope(root_scope)
    _ = (inner_scope, child_scope, root_scope)


def hash_table_demo() -> None:
    table = open_scope(None)

    entries = [
        ("count", "variable", "integer", 1),
        ("index", "variable", "integer", 2),
        ("result", "variable", "integer", 3),
        ("flag", "variable", "integer", 4),
        ("total", "variable", "real", 5),
        ("avg", "variable", "real", 6),
        ("sum", "variable", "real", 7),
        ("max", "variable", "integer", 8),
        ("min", "variable", "integer", 9),
        ("temp", "variable", "integer", 10),
    ]

    for label, category, data_type, line_no in entries:
        table.insert(label, category, data_type, lineno=line_no)

    for label in ["count", "index", "nothere1", "total", "nothere2"]:
        outcome = table.find(label)
        print(f"lookup {label} -> {'found' if outcome is not None else 'not found'}")

    for label in ["index", "total", "temp"]:
        removed = table.erase(label)
        print(f"delete {label} -> {'deleted' if removed else 'not found'}")

    print("Final table state:")
    table.render()


def main() -> None:
    print("=" * 60)
    print("SCENARIO 1: Pascal Program Simulation")
    print("=" * 60)
    nested_scope_demo()

    print()
    print("=" * 60)
    print("SCENARIO 2: Hash Table Stress Test")
    print("=" * 60)
    hash_table_demo()


if __name__ == "__main__":
    main()
