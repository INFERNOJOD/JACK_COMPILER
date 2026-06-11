import os
from SymbolTable import SymbolTable
from VMWriter    import VMWriter

# map operators to vm commands
OP_MAP = {
    "+": "add", "-": "sub", "*": None,
    "/": None,
    "&": "and", "|": "or",
    "<": "lt",  ">": "gt", "=": "eq",
}

UNARY_OP_MAP = {"-": "neg", "~": "not"}

XML_ESCAPE = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}


class CompilationEngine:
    """compiles one class into xml and vm"""

    def __init__(self, tokens: list[tuple[str, str]], source_path: str):
        self.tokens  = tokens
        self.pos     = 0

        base              = os.path.splitext(source_path)[0]
        self.xml_path     = base + ".xml"
        self.vm_path      = base + ".vm"

        self.xml_lines: list[str] = []
        self.indent      = 0

        self.symbol_table = SymbolTable()
        self.vm           = VMWriter(self.vm_path)

        self.class_name   = ""
        self._label_count = 0

    # basic token access functions

    def _peek(self) -> tuple[str, str]:
        return self.tokens[self.pos]

    def _advance(self) -> tuple[str, str]:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _expect(self, value: str) -> tuple[str, str]:
        """check and consume next token value"""
        tok = self._advance()
        if tok[1] != value:
            raise SyntaxError(f"Expected '{value}', got '{tok[1]}' at token {self.pos}")
        return tok

    def _expect_type(self, ttype: str) -> tuple[str, str]:
        """check and consume next token type"""
        tok = self._advance()
        if tok[0] != ttype:
            raise SyntaxError(f"Expected token type '{ttype}', got '{tok[0]}' ('{tok[1]}') at token {self.pos}")
        return tok

    def _peek_value(self) -> str:
        return self.tokens[self.pos][1]

    def _peek_type(self) -> str:
        return self.tokens[self.pos][0]

    # xml writing helpers

    def _xml_open(self, tag: str):
        self.xml_lines.append("  " * self.indent + f"<{tag}>")
        self.indent += 1

    def _xml_close(self, tag: str):
        self.indent -= 1
        self.xml_lines.append("  " * self.indent + f"</{tag}>")

    def _xml_token(self, ttype: str, value: str):
        for ch, esc in XML_ESCAPE.items():
            value = value.replace(ch, esc)
        self.xml_lines.append("  " * self.indent + f"<{ttype}> {value} </{ttype}>")

    def _write_token(self) -> tuple[str, str]:
        """write current token to xml file"""
        ttype, value = self._advance()
        self._xml_token(ttype, value)
        return ttype, value

    def _write_expected(self, value: str):
        """write expected value token to xml"""
        ttype, val = self._advance()
        if val != value:
            raise SyntaxError(f"Expected '{value}', got '{val}' at token {self.pos}")
        self._xml_token(ttype, val)

    def _write_expected_type(self, ttype: str) -> str:
        """write expected type token to xml"""
        t, v = self._advance()
        if t != ttype:
            raise SyntaxError(f"Expected type '{ttype}', got '{t}' ('{v}') at token {self.pos}")
        self._xml_token(t, v)
        return v

    # counter for unique vm labels

    def _new_label(self, prefix: str) -> str:
        self._label_count += 1
        return f"{prefix}_{self._label_count}"

    # compile the main class block

    def compile_class(self):
        """compile the whole class"""
        self._xml_open("class")

        self._write_expected("class")
        self.class_name = self._write_expected_type("identifier")
        self._write_expected("{")

        while self._peek_value() in ("static", "field"):
            self.compile_class_var_dec()

        while self._peek_value() in ("constructor", "function", "method"):
            self.compile_subroutine_dec()

        self._write_expected("}")
        self._xml_close("class")

        # save files
        with open(self.xml_path, "w") as f:
            f.write("\n".join(self.xml_lines) + "\n")
        print(f"[CompilationEngine] Parse tree → {self.xml_path}")
        self.vm.close()

    # compile static and field variables

    def compile_class_var_dec(self):
        """compile class variables"""
        self._xml_open("classVarDec")

        kind  = self._write_expected_type("keyword")
        typ   = self._compile_type()
        name  = self._write_expected_type("identifier")
        self.symbol_table.define(name, typ, kind)

        while self._peek_value() == ",":
            self._write_expected(",")
            name = self._write_expected_type("identifier")
            self.symbol_table.define(name, typ, kind)

        self._write_expected(";")
        self._xml_close("classVarDec")

    # compile functions and methods

    def compile_subroutine_dec(self):
        """compile subroutine declarations"""
        self._xml_open("subroutineDec")
        self.symbol_table.start_subroutine()

        sub_type = self._write_expected_type("keyword")
        self._compile_type(allow_void=True)
        sub_name = self._write_expected_type("identifier")

        # this is argument 0 for methods
        if sub_type == "method":
            self.symbol_table.define("this", self.class_name, "argument")

        self._write_expected("(")
        self._xml_open("parameterList")
        self.compile_parameter_list()
        self._xml_close("parameterList")
        self._write_expected(")")

        self.compile_subroutine_body(sub_name, sub_type)
        self._xml_close("subroutineDec")

    def compile_parameter_list(self):
        """compile the parameter list"""
        if self._peek_value() == ")":
            return
        typ  = self._compile_type()
        name = self._write_expected_type("identifier")
        self.symbol_table.define(name, typ, "argument")

        while self._peek_value() == ",":
            self._write_expected(",")
            typ  = self._compile_type()
            name = self._write_expected_type("identifier")
            self.symbol_table.define(name, typ, "argument")

    def compile_subroutine_body(self, sub_name: str, sub_type: str):
        """compile the subroutine body"""
        self._xml_open("subroutineBody")
        self._write_expected("{")

        while self._peek_value() == "var":
            self.compile_var_dec()

        n_locals = self.symbol_table.var_count("local")
        full_name = f"{self.class_name}.{sub_name}"
        self.vm.write_function(full_name, n_locals)

        # setup the this pointer
        if sub_type == "constructor":
            n_fields = self.symbol_table.var_count("field")
            self.vm.write_push("constant", n_fields)
            self.vm.write_call("Memory.alloc", 1)
            self.vm.write_pop("pointer", 0)
        elif sub_type == "method":
            self.vm.write_push("argument", 0)
            self.vm.write_pop("pointer", 0)

        self.compile_statements()
        self._write_expected("}")
        self._xml_close("subroutineBody")

    def compile_var_dec(self):
        """compile local variable declarations"""
        self._xml_open("varDec")
        self._write_expected("var")
        typ  = self._compile_type()
        name = self._write_expected_type("identifier")
        self.symbol_table.define(name, typ, "local")

        while self._peek_value() == ",":
            self._write_expected(",")
            name = self._write_expected_type("identifier")
            self.symbol_table.define(name, typ, "local")

        self._write_expected(";")
        self._xml_close("varDec")

    # compile different types of statements

    def compile_statements(self):
        """compile the statement block"""
        self._xml_open("statements")
        while self._peek_value() in ("let", "if", "while", "do", "return"):
            v = self._peek_value()
            if   v == "let":    self.compile_let()
            elif v == "if":     self.compile_if()
            elif v == "while":  self.compile_while()
            elif v == "do":     self.compile_do()
            elif v == "return": self.compile_return()
        self._xml_close("statements")

    def compile_let(self):
        """compile let statements"""
        self._xml_open("letStatement")
        self._write_expected("let")
        name = self._write_expected_type("identifier")

        is_array = self._peek_value() == "["
        if is_array:
            # push array base address
            seg = VMWriter.kind_to_segment(self.symbol_table.kind_of(name))
            idx = self.symbol_table.index_of(name)
            self.vm.write_push(seg, idx)

            self._write_expected("[")
            self.compile_expression()
            self._write_expected("]")

            self.vm.write_arithmetic("add")

        self._write_expected("=")
        self.compile_expression()
        self._write_expected(";")

        if is_array:
            # pointer 1 idiom for array writes
            self.vm.write_pop("temp", 0)
            self.vm.write_pop("pointer", 1)
            self.vm.write_push("temp", 0)
            self.vm.write_pop("that", 0)
        else:
            seg = VMWriter.kind_to_segment(self.symbol_table.kind_of(name))
            idx = self.symbol_table.index_of(name)
            self.vm.write_pop(seg, idx)

        self._xml_close("letStatement")

    def compile_if(self):
        """compile if else statements"""
        self._xml_open("ifStatement")
        label_false = self._new_label("IF_FALSE")
        label_end   = self._new_label("IF_END")

        self._write_expected("if")
        self._write_expected("(")
        self.compile_expression()
        self._write_expected(")")

        self.vm.write_arithmetic("not")
        self.vm.write_if(label_false)

        self._write_expected("{")
        self.compile_statements()
        self._write_expected("}")

        self.vm.write_goto(label_end)
        self.vm.write_label(label_false)

        if self._peek_value() == "else":
            self._write_expected("else")
            self._write_expected("{")
            self.compile_statements()
            self._write_expected("}")

        self.vm.write_label(label_end)
        self._xml_close("ifStatement")

    def compile_while(self):
        """compile while loop statements"""
        self._xml_open("whileStatement")
        label_top  = self._new_label("WHILE_TOP")
        label_end  = self._new_label("WHILE_END")

        self.vm.write_label(label_top)

        self._write_expected("while")
        self._write_expected("(")
        self.compile_expression()
        self._write_expected(")")

        self.vm.write_arithmetic("not")
        self.vm.write_if(label_end)

        self._write_expected("{")
        self.compile_statements()
        self._write_expected("}")

        self.vm.write_goto(label_top)
        self.vm.write_label(label_end)
        self._xml_close("whileStatement")

    def compile_do(self):
        """compile do statements"""
        self._xml_open("doStatement")
        self._write_expected("do")
        name = self._write_expected_type("identifier")
        self._compile_subroutine_call(name)
        self._write_expected(";")
        
        # discard the return value
        self.vm.write_pop("temp", 0)
        self._xml_close("doStatement")

    def compile_return(self):
        """compile return statements"""
        self._xml_open("returnStatement")
        self._write_expected("return")

        if self._peek_value() != ";":
            self.compile_expression()
        else:
            # push 0 for void returns
            self.vm.write_push("constant", 0)

        self._write_expected(";")
        self.vm.write_return()
        self._xml_close("returnStatement")

    # compile mathematical and logical expressions

    def compile_expression(self):
        """compile a full expression"""
        self._xml_open("expression")
        self.compile_term()

        while self._peek_value() in OP_MAP:
            op = self._peek_value()
            self._write_token()
            self.compile_term()

            vm_op = OP_MAP[op]
            if vm_op:
                self.vm.write_arithmetic(vm_op)
            elif op == "*":
                self.vm.write_call("Math.multiply", 2)
            elif op == "/":
                self.vm.write_call("Math.divide", 2)

        self._xml_close("expression")

    def compile_term(self):
        """compile a single term"""
        self._xml_open("term")
        ttype, value = self._peek()

        # push integer constant
        if ttype == "integerConstant":
            self._write_token()
            self.vm.write_push("constant", int(value))

        # allocate and append string chars
        elif ttype == "stringConstant":
            self._write_token()
            self.vm.write_push("constant", len(value))
            self.vm.write_call("String.new", 1)
            for ch in value:
                self.vm.write_push("constant", ord(ch))
                self.vm.write_call("String.appendChar", 2)

        # handle true false null this
        elif ttype == "keyword" and value in ("true", "false", "null", "this"):
            self._write_token()
            if value == "true":
                self.vm.write_push("constant", 0)
                self.vm.write_arithmetic("not")
            elif value in ("false", "null"):
                self.vm.write_push("constant", 0)
            elif value == "this":
                self.vm.write_push("pointer", 0)

        # handle grouped expressions
        elif value == "(":
            self._write_expected("(")
            self.compile_expression()
            self._write_expected(")")

        # handle unary operators
        elif value in UNARY_OP_MAP:
            self._write_token()
            self.compile_term()
            self.vm.write_arithmetic(UNARY_OP_MAP[value])

        # handle arrays and subroutine calls
        elif ttype == "identifier":
            name = self._write_expected_type("identifier")
            next_val = self._peek_value()

            # direct array access
            if next_val == "[":
                seg = VMWriter.kind_to_segment(self.symbol_table.kind_of(name))
                idx = self.symbol_table.index_of(name)
                self.vm.write_push(seg, idx)

                self._write_expected("[")
                self.compile_expression()
                self._write_expected("]")

                self.vm.write_arithmetic("add")
                self.vm.write_pop("pointer", 1)
                self.vm.write_push("that", 0)

            # direct subroutine call
            elif next_val in ("(", "."):
                self._compile_subroutine_call(name)

            # standard variable push
            else:
                kind = self.symbol_table.kind_of(name)
                if kind:
                    seg = VMWriter.kind_to_segment(kind)
                    idx = self.symbol_table.index_of(name)
                    self.vm.write_push(seg, idx)

        self._xml_close("term")

    def compile_expression_list(self) -> int:
        """compile comma separated expressions"""
        self._xml_open("expressionList")
        n = 0
        if self._peek_value() != ")":
            self.compile_expression()
            n = 1
            while self._peek_value() == ",":
                self._write_expected(",")
                self.compile_expression()
                n += 1
        self._xml_close("expressionList")
        return n

    # helper for compiling method calls

    def _compile_subroutine_call(self, name: str):
        """compile direct or object method calls"""
        n_args = 0

        if self._peek_value() == "(":
            # implicit call on current object
            self.vm.write_push("pointer", 0)
            n_args += 1
            self._write_expected("(")
            n_args += self.compile_expression_list()
            self._write_expected(")")
            self.vm.write_call(f"{self.class_name}.{name}", n_args)

        elif self._peek_value() == ".":
            # call on specific object or class
            self._write_expected(".")
            method_name = self._write_expected_type("identifier")

            if self.symbol_table.contains(name):
                # object method call
                kind = self.symbol_table.kind_of(name)
                seg  = VMWriter.kind_to_segment(kind)
                idx  = self.symbol_table.index_of(name)
                typ  = self.symbol_table.type_of(name)
                self.vm.write_push(seg, idx)
                n_args += 1
                self._write_expected("(")
                n_args += self.compile_expression_list()
                self._write_expected(")")
                self.vm.write_call(f"{typ}.{method_name}", n_args)
            else:
                # static function or constructor call
                self._write_expected("(")
                n_args += self.compile_expression_list()
                self._write_expected(")")
                self.vm.write_call(f"{name}.{method_name}", n_args)

    # helper for parsing variable types

    def _compile_type(self, allow_void: bool = False) -> str:
        """parse and return variable type"""
        ttype, value = self._peek()
        primitives = {"int", "char", "boolean"}
        if allow_void:
            primitives.add("void")

        if ttype == "keyword" and value in primitives:
            self._write_token()
        elif ttype == "identifier":
            self._write_token()
        else:
            raise SyntaxError(f"Expected type, got '{value}' at token {self.pos}")
        return value