# Compiler Lab

## Files

- `src/scope_table.py` - chained hash table, nested scope support, lookup, delete, and pretty printing.
- `demo_driver.py` - two end-to-end scenarios that exercise insertion, lookup, deletion, shadowing, and error reporting.
- `report.tex` - detailed LaTeX report for the five test cases.
- `test/` - plain-text test fixtures for the five lab cases.
- `output/` - captured output for each test fixture.

## How to run

From this folder:

```bash
python demo_driver.py
```

## What is covered

- Task 1: fixed-size hash table with separate chaining.
- Task 2: begin-scope and end-scope stack behavior.
- Task 3: duplicate declaration and undeclared-name handling.
- Task 4: aligned tabular scope printing.
- Task 5: written test report in LaTeX.
