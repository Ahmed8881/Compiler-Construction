# Lab 13 Symbol Table Manager

This submission implements a hash-based symbol table with nested scope handling for the Pascal subset used in the compiler construction labs.

## Files

- `src/symtable.py` - symbol table implementation, hash function, scope helpers, and pretty printing.
- `test_driver.py` - two test scenarios that exercise insert, lookup, delete, begin_scope, and end_scope.
- `requirements.txt` - empty dependency list; the project uses only the Python standard library.

## How to run

From the `Lab11/submission` folder:

```bash
python test_driver.py
```

## How the parser from the previous lab can use this module

Import the scope helpers and symbol table into the recursive-descent parser, then call them at the grammar points where declarations and uses occur.

- Rule 1 (`program`) - call `begin_scope(None)` for the global scope before parsing the program body.
- Rule 3 (`declarations`) - call `insert` for each declared variable name.
- Rule 7 (`subprogram_declaration`) - call `begin_scope` before the subprogram body and `end_scope` after it finishes.
- Rule 8 (`subprogram_head`) - call `insert` for the function or procedure name in the enclosing scope.
- Rule 10 (`parameter_list`) - call `insert` for each formal parameter.
- Rule 14 (`statement` / assignment) - call `lookup` before using a variable on the left or right side of an assignment.
- Rule 15 (`variable`) - call `lookup` when a variable reference is parsed.
- Rule 21 (`factor` / id) - call `lookup` when an identifier appears as a factor or function call.

A simple integration pattern is to keep a `current_scope` variable inside the parser, update it with `begin_scope` / `end_scope`, and pass it to `insert` and `lookup` whenever the grammar reaches a declaration or use site.

## Expected behavior

- Duplicate names in the same scope are rejected.
- Lookups search outward through parent scopes.
- End-of-scope dumps are printed in line-number order.
- All errors are written with `sys.stderr.write()`.

## Python-specific pitfall

The C version needs `strdup()` because the lexer buffer can be reused or overwritten after insertion. Python strings are immutable, so the lexeme value does not need manual duplication for safety. The symbol table still stores its own `Entry.name` value so each entry keeps the exact identifier text even after the parser moves on to the next token.
