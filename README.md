# Mini Compiler (CSE 430)

A small educational mini-compiler implemented in Python with a simple GUI. This project demonstrates the core components of a compiler pipeline: lexical analysis, parsing with semantic checks and scope tracking, intermediate code generation, a toy assembly generator, and a Tkinter GUI for interactive compilation and inspection.

This code was written as part of a compiler course (CSE 430) and is meant primarily for learning and demonstration.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the GUI](#running-the-gui)
- [Usage](#usage)
- [What you see in the UI / Output](#what-you-see-in-the-ui--output)
- [Project Structure & Components](#project-structure--components)
- [Grammar (high level)](#grammar-high-level)
- [Example source code](#example-source-code)
- [Limitations & TODO](#limitations--todo)
- [Contributing](#contributing)
- [License](#license)

## Features

- Lexical analyzer using PLY (lex)
  - Tokenizes identifiers, integers, floats, operators, punctuation and handles single- and multi-line comments.
- Parser using PLY (yacc)
  - Recognizes variable declarations, assignments, arithmetic expressions, if/else, while, print statements and scoped blocks.
- Symbol table with scope tracking (scoped variables)
  - Tracks declarations per scope and detects redeclarations or undeclared uses.
- Intermediate code (three-address-like) generation
  - Emits temporaries and labels for control flow and expressions.
- Simple assembly-like code generator (toy instructions)
- Tkinter GUI to input code and view:
  - Tokens, Symbol Table, Intermediate Code, Generated Assembly, Errors
- Example sample source code pre-filled in the GUI.

## Requirements

- Python 3.8+
- Dependencies:
  - ply
  - tkinter (usually included with standard Python on most platforms)

Install PLY:

```bash
pip install ply
```

Note: tkinter is part of the standard library on many systems. On some Linux distributions you may need to install a separate package (e.g. `sudo apt install python3-tk`).

## Installation

Clone the repository:

```bash
git clone https://github.com/SamiulUtshaw/Mini-Compiler.git
cd Mini-Compiler
```

Place the provided Python file (the GUI + compiler implementation) in the repo root or run it from its current location.

## Running the GUI

Assuming the script file containing the code is named `mini_compiler.py` (or the name you have in the repo), run:

```bash
python mini_compiler.py
```

This launches a window titled "CSE 430 - Mini Compiler". The top pane is where you write/source code. The bottom pane has tabs for:
- Tokens
- Symbol Table
- Intermediate Code
- Assembly
- Errors

Click "Compile" to run the lexer, parser, semantic checks and code generator over the current source buffer.

## Usage

1. Edit the sample or type new source code in the "Source Code" pane.
2. Click "Compile".
3. Read outputs in the tabs:
   - Tokens — lexical tokens produced.
   - Symbol Table — declared symbols and their scopes.
   - Intermediate Code — emitted 3-address-like instructions.
   - Assembly — toy assembly generated from intermediate code.
   - Errors — lexical / syntax / semantic errors found.

Use "Clear All" to clear the editor and outputs.

## What you see in the UI / Output

- Tokens: lists token type, value and line number.
- Symbol Table: name / type / scope. Scopes are tracked as `global` and generated `scope_N` names for block scopes.
- Intermediate Code: numbered, three-address-style instructions (assignments, arithmetic ops, labels, gotos).
- Assembly: toy assembly instruction sequence produced by the CodeGenerator class.
- Errors: combined lexical and parser/semantic errors (undeclared variables, redeclarations, syntax issues).

## Project Structure & Components (high level)

- Lexer (class Lexer)
  - Token rules for identifiers, numbers, floats, operators, punctuation
  - Handles `//` single-line and `/* */` multi-line comments
- SymbolTable (class SymbolTable)
  - Insert/lookup per-scope, enter/exit scope
- Parser & Semantic Analyzer (class Parser)
  - PLY-based grammar rules for declarations, statements, expressions, control flow
  - Emits intermediate code via emit()
  - Builds temporaries and labels
- ScopeTrackingLexer
  - Extends Lexer to enter/exit scopes when `{` / `}` tokens are encountered
- CodeGenerator (class CodeGenerator)
  - Maps intermediate instructions to a toy assembly with registers and simple instructions
- CompilerGUI
  - Tkinter-based graphical interface for editing, compiling and inspecting outputs

## Grammar (high level BNF-like)

- program -> statement_list
- statement_list -> statement_list statement | statement
- statement -> declaration | assignment | print_statement | if_statement | while_statement | block
- declaration -> type ID ';' | type ID '=' expression ';'
- type -> 'int' | 'float'
- assignment -> ID '=' expression ';'
- print_statement -> 'print' '(' expression ')' ';'
- if_statement -> 'if' '(' condition ')' block ( 'else' block )?
- while_statement -> 'while' '(' condition ')' block
- condition -> expression relop expression
- relop -> '<' | '<=' | '>' | '>=' | '==' | '!='
- expression -> expression '+' term | expression '-' term | term
- term -> term '*' factor | term '/' factor | term '%' factor | factor
- factor -> NUMBER | FLOAT_NUM | ID | '(' expression ')'
- block -> '{' statement_list '}'

This grammar and the parser implementation are intentionally limited to keep the code concise and instructional.

## Example source code

Here is the sample code pre-loaded into the GUI (also useful as a quick test):

```c
// Global variables
int x;
int y;
x = 10;
y = 20;

/* Calculate sum */
int sum;
sum = x + y;
print(sum);

// If block with local scope
if (x < y) {
    int diff;  // Local to if block
    diff = y - x;
    print(diff);
}

// While loop with local scope
int counter;
counter = 0;
while (counter < 5) {
    int temp;  // Local to while block
    temp = counter * 2;
    counter = counter + 1;
}
```

## Limitations & TODO

- Toy subset of a language — no functions, arrays, pointers, complex types, or scoping beyond block-level.
- Error recovery in the parser is minimal (syntax errors are reported but recovery is basic).
- Assembly generation is illustrative and not executable on a real CPU.
- No optimization passes.
- Improvements to consider:
  - Add function/procedure support
  - Add better type checking/conversion for arithmetic mixing int/float
  - Improve code generation to generate real executable (e.g., LLVM IR or actual assembler)
  - Add unit tests and CI integration
  - Save / load projects and files from GUI

## Contributing

Contributions are welcome. If you'd like to add features, fixes or improvements:
1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Implement changes and tests
4. Open a pull request describing the changes

If you want, tell me how you want it committed and I can prepare the commit message and changes.

## License

This project is provided for educational purposes. You can add an OSS license you prefer (MIT is common for small educational projects).

---

If you'd like, I can add this README.md to your repository (create a commit on `main` or open a branch + pull request). Tell me where you'd like it added and whether you'd like an MIT license file added as well.
