import os
import sys
from JackTokenizer    import JackTokenizer
from CompilationEngine import CompilationEngine


def compile_file(jack_path: str):
    """compile a single jack file"""
    print(f"\n── Compiling {jack_path} ──")

    # run the tokenizer
    tokenizer = JackTokenizer(jack_path)
    tokens    = tokenizer.tokenize()

    # run the parser
    engine = CompilationEngine(tokens, jack_path)
    engine.compile_class()


def main():
    if len(sys.argv) < 2:
        print("Usage: python JackCompiler.py <file.jack | directory>")
        sys.exit(1)

    path = sys.argv[1]

    if os.path.isdir(path):
        jack_files = [
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.endswith(".jack")
        ]
        if not jack_files:
            print(f"No .jack files found in {path}")
            sys.exit(1)
        for jf in sorted(jack_files):
            compile_file(jf)
    elif path.endswith(".jack"):
        compile_file(path)
    else:
        print("Error: input must be a .jack file or a directory containing .jack files")
        sys.exit(1)

    print("\nCompilation complete.")


if __name__ == "__main__":
    main()