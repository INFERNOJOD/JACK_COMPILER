# JackTokenizer.py
# Converts Jack source files into classified tokens

import re
import os

# Jack language keywords and symbols

KEYWORDS = {
    "class", "constructor", "function", "method", "field", "static",
    "var", "int", "char", "boolean", "void", "true", "false", "null",
    "this", "let", "do", "if", "else", "while", "return"
}

SYMBOLS = set("{}()[].,;+-*/&|<>=~")

# Escape special XML characters
XML_ESCAPE = {
    "<":  "&lt;",
    ">":  "&gt;",
    "&":  "&amp;",
    '"':  "&quot;",
    "'":  "&apos;",
}


class JackTokenizer:
    # Takes a Jack source file and tokenizes it

    def __init__(self, filepath: str):
        self.filepath = filepath
        # Generate XML filename from input file
        base = os.path.splitext(filepath)[0]
        self.xml_path = base + "T.xml"
        self.tokens: list[tuple[str, str]] = []

    # Main tokenizing function

    def tokenize(self) -> list[tuple[str, str]]:
        # Read file, remove comments, tokenize
        with open(self.filepath, "r") as f:
            source = f.read()

        clean = self._strip_comments(source)
        self.tokens = self._lex(clean)
        self._write_xml()
        return self.tokens

    # Remove comments from source code

    def _strip_comments(self, source: str) -> str:
        # Remove //, /* */ style comments
        CODE, LINE_CMT, BLOCK_CMT, STRING = 0, 1, 2, 3
        state = CODE  # Track parsing state
        result = []
        i = 0
        n = len(source)

        while i < n:
            ch = source[i]

            if state == CODE:
                if ch == '"':
                    # Found string literal, keep it
                    state = STRING
                    result.append(ch)
                    i += 1
                elif ch == '/' and i + 1 < n and source[i + 1] == '/':
                    # Single line comment starts
                    state = LINE_CMT
                    i += 2
                elif ch == '/' and i + 1 < n and source[i + 1] == '*':
                    # Block comment starts
                    state = BLOCK_CMT
                    i += 2
                else:
                    result.append(ch)
                    i += 1

            elif state == LINE_CMT:
                if ch == '\n':
                    # Newline ends the comment
                    state = CODE
                    result.append('\n')
                i += 1

            elif state == BLOCK_CMT:
                if ch == '*' and i + 1 < n and source[i + 1] == '/':
                    # Block comment ends here
                    state = CODE
                    i += 2
                else:
                    # Skip comment content
                    if ch == '\n':
                        result.append('\n')
                    i += 1

            elif state == STRING:
                result.append(ch)
                if ch == '"':
                    # String ends, back to code
                    state = CODE
                i += 1

        return "".join(result)

    # Tokenize the cleaned source code

    def _lex(self, source: str) -> list[tuple[str, str]]:
        # Convert source into tokens and their types
        tokens = []
        i = 0
        n = len(source)

        while i < n:
            ch = source[i]
            # Skip whitespace characters
            if ch in " \t\r\n":
                i += 1
                continue

            # Check for string constants
            if ch == '"':
                j = i + 1
                while j < n and source[j] != '"':
                    j += 1
                # Store string without quotes
                tokens.append(("stringConstant", source[i + 1: j]))
                i = j + 1
                continue

            # Check if it's a symbol
            if ch in SYMBOLS:
                tokens.append(("symbol", ch))
                i += 1
                continue

            # Check for integer constants
            if ch.isdigit():
                j = i
                while j < n and source[j].isdigit():
                    j += 1
                val = source[i:j]
                if not (0 <= int(val) <= 32767):
                    raise ValueError(f"Integer constant {val} out of range [0, 32767]")
                tokens.append(("integerConstant", val))
                i = j
                continue

            # Check for keywords or identifiers
            if ch.isalpha() or ch == '_':
                j = i
                while j < n and (source[j].isalnum() or source[j] == '_'):
                    j += 1
                word = source[i:j]
                if word in KEYWORDS:
                    tokens.append(("keyword", word))
                else:
                    tokens.append(("identifier", word))
                i = j
                continue

            # Unknown character, skip it
            print(f"[JackTokenizer] WARNING: unknown character '{ch}' at position {i}, skipping.")
            i += 1

        return tokens

    # Write tokens to XML file

    def _escape(self, value: str) -> str:
        # Escape XML special characters
        value = value.replace("&", "&amp;")
        value = value.replace("<", "&lt;")
        value = value.replace(">", "&gt;")
        value = value.replace('"', "&quot;")
        return value

    def _write_xml(self):
        # Save tokens to XML output file
        lines = ["<tokens>"]
        for token_type, value in self.tokens:
            escaped = self._escape(value)
            lines.append(f"  <{token_type}> {escaped} </{token_type}>")
        lines.append("</tokens>")

        with open(self.xml_path, "w") as f:
            f.write("\n".join(lines) + "\n")

        print(f"Wrote {len(self.tokens)} tokens to {self.xml_path}")


# Run tokenizer from command line

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python JackTokenizer.py <file.jack>")
        sys.exit(1)

    path = sys.argv[1]
    if not path.endswith(".jack"):
        print("Error: input file must be a .jack file")
        sys.exit(1)

    t = JackTokenizer(path)
    toks = t.tokenize()
    print(f"Tokenized {len(toks)} tokens.")
