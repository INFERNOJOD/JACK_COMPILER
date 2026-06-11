DA2304 Assignment 3 - Jack Compiler
Name : Krish Yadav
Roll No : DA24B043

This is the Jack to VM compiler for Assignment 3 . It reads the Jack files and generates the corresponding XML syntax trees and VM code .

Files in the src directory :
- JackTokenizer.py : Reads the raw jack code, strips comments, and generates the T.xml token files .
- CompilationEngine.py : The recursive descent parser. It reads the tokens and generates the final .xml tree and the .vm code .
- SymbolTable.py : Tracks the class and subroutine scopes for all variables .
- VMWriter.py : Helper class that writes the actual VM commands .
- JackCompiler.py : The main runner that wires everything together .

How to run the code :
You just need Python 3 to run this . No external libraries are needed .

To compile everything at once, run this command :
python3 JackCompiler.py ../jack/

To compile just a single file, run :
python3 JackCompiler.py ../jack/Conv.jack

This will output the T.xml, .xml, and .vm files into the same directory . You can then load those .vm files directly into the Hack VM Emulator, or pass them into the Assignment 2 VM Translator to get the assembly code .

Design Notes :
- I set the default stride to S = 1 in the Conv class .
- I used a Laplacian edge detection kernel for the filter ( 0,-1,0 / -1,4,-1 / 0,-1,0 ) .
- Array writes are handled using the standard pop temp 0 / pop pointer 1 idiom so the address isn't lost .