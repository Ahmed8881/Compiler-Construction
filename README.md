# Compiler Construction Labs: Lab 7 and Lab 8

This repository includes two related parsing labs:
- **Lab 7**: Recursive Descent Parsing
- **Lab 8**: LL(1) Parsing (table-driven predictive parsing)

You mentioned you have **4 parsers**. In this project, they can be understood as the following 4 parser components/programs.

## Parser 1: Recursive Descent Parser (Lab 7)
**File:** `Lab7/recursive_descent.py`

### What it is
A hand-written top-down parser for the Pascal-like grammar. Each non-terminal is implemented as a Python method (`program`, `statement`, `expression`, etc.).

### How it works
- Uses a custom `Lexer` to tokenize source code.
- Uses methods like `expect`, `match`, and `check` to consume tokens.
- Reports syntax errors with line numbers using `ParseError`.

### Key features
- Supports declarations, procedures/functions, compound statements, `if-then-else`, `while-do`, expressions, arrays, and procedure calls.
- Clear grammar-to-code mapping (easy to learn and debug).

### Run
```powershell
python Lab7/recursive_descent.py
```
Or parse a file:
```powershell
python Lab7/recursive_descent.py path_to_pascal_file.pas
```

---

## Parser 2: Predictive Parse Engine (Algorithm 4.34) (Lab 8)
**File:** `Lab8/task4_algorithm_4_34.py`

### What it is
A **table-driven predictive parser core** that implements Algorithm 4.34 using:
- parsing stack
- input pointer
- LL(1) parse table

### How it works
- `tokenize_input()` converts raw text into grammar terminals (`id`, `num`, `assignop`, `relop`, etc.).
- `table_driven_predictive_parse()` performs stack-based parsing.
- Optional trace output shows: stack, remaining input, and parser action.

### Key features
- Deterministic LL(1) parsing.
- Produces leftmost derivation steps.
- Returns clear error reasons like missing table entry or token mismatch.

---

## Parser 3: LL(1) Parser Class (Lab 8)
**File:** `Lab8/task5_ll1_parser.py`

### What it is
A high-level parser class (`LL1Parser`) that builds everything needed and then parses strings.

### How it works
- Loads grammar from `grammar_ll1.txt`.
- Computes FIRST and FOLLOW sets.
- Builds parse table.
- Checks conflicts (rejects grammar if not LL(1)).
- Calls the Algorithm 4.34 parse engine for actual parsing.

### Key features
- Clean API: `parse_string(source, trace=False)`
- Combines grammar validation + parsing in one reusable class.

---

## Parser 4: Interactive LL(1) Parser Driver (Lab 8)
**File:** `Lab8/LL1.py`

### What it is
User-facing parser program that runs your LL(1) pipeline end-to-end from terminal input.

### Flow
1. Validates LL(1) grammar.
2. Creates `LL1Parser`.
3. Accepts user input string.
4. Optionally shows Algorithm 4.34 trace.
5. Prints `Valid/Invalid` and the leftmost derivation productions used.

### Run
```powershell
python Lab8/LL1.py
```

---

## Supporting Lab 8 Modules
- `Lab8/task1_make_ll1_grammar.py`: Grammar LL(1) validation report.
- `Lab8/task2_first_follow.py`: FIRST/FOLLOW computation.
- `Lab8/task3_parsing_table.py`: Parse table construction and conflict reporting.
- `Lab8/ll1_grammar.py`: Grammar loader (`grammar_ll1.txt`).

---

## Lab 7 vs Lab 8 (Quick Comparison)
- **Lab 7 (Recursive Descent):** Rules are hardcoded as methods; very readable for learning parser construction.
- **Lab 8 (LL(1) Table-Driven):** More formal and scalable; parser behavior comes from grammar + parse table.

In short:
- Lab 7 teaches manual parser design.
- Lab 8 teaches automated predictive parsing using LL(1) theory.
