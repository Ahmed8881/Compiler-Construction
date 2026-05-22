from __future__ import annotations
import sys
from src.symtable import SymTable, begin_scope, end_scope


def emit_error(message: str) -> None:
    sys.stderr.write(message + "\n")


def scenario1() -> None:
    global_scope = begin_scope(None)
    global_scope.insert("myProg", "function", "integer", line=1)
    global_scope.insert("input", "parameter", "integer", line=1)
    global_scope.insert("output", "parameter", "integer", line=1)
    global_scope.insert("x", "variable", "integer", line=2)
    global_scope.insert("y", "variable", "integer", line=3)

    func_scope = begin_scope(global_scope)
    func_scope.insert("a", "parameter", "integer", line=4)
    func_scope.insert("b", "parameter", "integer", line=4)

    inner_scope = begin_scope(func_scope)
    inner_scope.insert("z", "variable", "integer", line=6)

    result = inner_scope.lookup("x")
    if result is not None:
        print(f"[Scope 2] lookup x -> found at scope {result.scope_level}")

    result = inner_scope.lookup("y")
    if result is not None:
        print(f"[Scope 2] lookup y -> found at scope {result.scope_level}")

    inner_scope.insert("x", "variable", "integer", line=8)
    result = inner_scope.lookup("x")
    if result is not None:
        print(f"[Scope 2] lookup x -> found at scope {result.scope_level} after shadowing")
    inner_scope = end_scope(inner_scope)

    func_scope = end_scope(func_scope)

    global_scope.insert("x", "variable", "integer", line=11)
    result = global_scope.lookup("a")
    if result is None:
        emit_error("ERROR line 12: undeclared variable 'a'")

    global_scope = end_scope(global_scope)
    _ = global_scope


def scenario2() -> None:
    table = begin_scope(None)

    inserts = [
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

    for name, kind, type_, line in inserts:
        table.insert(name, kind, type_, line=line)

    for name in ["count", "index", "nothere1", "total", "nothere2"]:
        result = table.lookup(name)
        print(f"lookup {name} -> {'found' if result is not None else 'not found'}")

    for name in ["index", "total", "temp"]:
        deleted = table.delete(name)
        print(f"delete {name} -> {'deleted' if deleted else 'not found'}")

    print("Final table state:")
    table.print_table()


def main() -> None:
    print("=" * 60)
    print("SCENARIO 1: Pascal Program Simulation")
    print("=" * 60)
    scenario1()

    print()
    print("=" * 60)
    print("SCENARIO 2: Hash Table Stress Test")
    print("=" * 60)
    scenario2()


if __name__ == "__main__":
    main()
