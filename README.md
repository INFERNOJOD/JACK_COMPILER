# Jack Compiler

A complete Jack-to-VM compiler implemented in Python as part of the Nand2Tetris toolchain.

This project translates programs written in the Jack programming language into Hack Virtual Machine (VM) instructions. The compiler performs lexical analysis, syntax analysis, symbol management and VM code generation using a recursive-descent parsing approach.

---

## Overview

The Jack programming language is a high-level object-oriented language designed for the Nand2Tetris educational computer system.

The objective of this project was to build a compiler capable of translating Jack source code into executable VM instructions that can later be translated into Hack Assembly and machine code.

The compiler supports:

- Class declarations
- Constructors
- Functions and methods
- Variable declarations
- Control flow statements
  - if
  - if-else
  - while
- Expressions and operators
- Arrays
- String constants
- Subroutine calls
- Object-oriented features of Jack

---

## Features

### Lexical Analysis

The tokenizer reads Jack source files and converts them into classified tokens.

Supported token types:

- Keywords
- Symbols
- Identifiers
- Integer constants
- String constants

The tokenizer also:

- Removes single-line comments
- Removes multi-line comments
- Ignores unnecessary whitespace

---

### Syntax Analysis

A recursive-descent parser is used to construct the complete parse tree of the program.

The parser validates:

- Class structure
- Variable declarations
- Statements
- Expressions
- Function calls
- Nested program constructs

XML parse trees are generated for debugging and verification.

---

### Symbol Table Management

The compiler maintains separate symbol tables for:

- Class scope
- Subroutine scope

Information tracked:

- Variable name
- Type
- Kind
- Running index

Supported variable categories:

- static
- field
- argument
- local

---

### VM Code Generation

The compiler generates Hack VM instructions corresponding to the source program.

Supported VM operations:

- Arithmetic commands
- Memory access commands
- Function calls
- Function declarations
- Returns
- Labels
- Conditional branching
- Loops

---

## Project Structure

```text
jack-compiler/
│
├── src/
│   ├── JackCompiler.py
│   ├── JackTokenizer.py
│   ├── CompilationEngine.py
│   ├── SymbolTable.py
│   └── VMWriter.py
│
├── examples/
│   ├── Main.jack
│   └── Conv.jack
│
├── outputs/
│   ├── Main.xml
│   ├── Main.vm
│   ├── Conv.xml
│   └── Conv.vm
│
├── report.pdf
└── README.md
```

---

## Compiler Components

### JackTokenizer.py

Responsible for:

- Reading Jack source code
- Removing comments
- Tokenizing source files
- Generating token XML files

Output:

```text
XXXT.xml
```

---

### CompilationEngine.py

Core recursive-descent parser.

Responsible for:

- Parsing tokens
- Building syntax trees
- Semantic processing
- Generating VM code

Outputs:

```text
XXX.xml
XXX.vm
```

---

### SymbolTable.py

Maintains identifier information during compilation.

Tracks:

- Scope
- Variable type
- Variable category
- Variable index

---

### VMWriter.py

Provides helper methods for generating VM commands.

Examples:

```vm
push constant 5
pop local 0
call Math.multiply 2
return
```

---

### JackCompiler.py

Main driver program.

Coordinates:

- Tokenization
- Parsing
- Symbol management
- VM generation

---

## Example Application

To verify correctness, the compiler was tested using a custom implementation of 2D convolution written entirely in Jack.

The application:

- Creates input matrices
- Creates convolution filters
- Performs convolution operations
- Generates output matrices

A Laplacian edge-detection kernel was used during testing.

This serves as a realistic end-to-end validation of the compiler pipeline.

---

## Requirements

Python 3.8+

No external libraries are required.

---

## Running the Compiler

### Compile a Single Jack File

```bash
python3 src/JackCompiler.py examples/Conv.jack
```

### Compile an Entire Directory

```bash
python3 src/JackCompiler.py examples/
```

Generated files:

```text
T.xml   -> Token stream
.xml    -> Parse tree
.vm     -> VM instructions
```

---

## Sample Workflow

```text
Jack Source Code
        │
        ▼
Tokenization
        │
        ▼
Syntax Analysis
        │
        ▼
Symbol Resolution
        │
        ▼
VM Code Generation
        │
        ▼
Hack VM Program
```

---

## Results

The compiler successfully generates:

- Token XML files
- Parse-tree XML files
- Executable Hack VM code

The generated VM programs can be executed using the Nand2Tetris VM Emulator.

---

## Technologies Used

- Python
- Recursive Descent Parsing
- Compiler Construction
- Symbol Table Design
- Stack-Based Virtual Machines
- Nand2Tetris Toolchain

---

## Course Information

Course: DA2304 – Computer Systems Design

Assignment: Jack Compiler and 2D Convolution

Institution: IIT Madras

---

## Author

Krish Yadav  
DA24B043
