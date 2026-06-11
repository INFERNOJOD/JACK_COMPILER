class VMWriter:
    # emits hack vm commands

    def __init__(self, output_path: str):
        self.output_path = output_path
        self._lines: list[str] = []

    # write push and pop commands

    def write_push(self, segment: str, index: int):
        # push to segment
        self._emit(f"push {segment} {index}")

    def write_pop(self, segment: str, index: int):
        # pop from segment
        self._emit(f"pop {segment} {index}")

    # write math and logic commands

    def write_arithmetic(self, command: str):
        # write alu command
        self._emit(command)

    # write branching commands

    def write_label(self, label: str):
        self._emit(f"label {label}")

    def write_goto(self, label: str):
        self._emit(f"goto {label}")

    def write_if(self, label: str):
        self._emit(f"if-goto {label}")

    # write function commands

    def write_function(self, name: str, n_locals: int):
        self._emit(f"function {name} {n_locals}")

    def write_call(self, name: str, n_args: int):
        self._emit(f"call {name} {n_args}")

    def write_return(self):
        self._emit("return")

    # helper functions

    def _emit(self, line: str):
        self._lines.append(line)

    def close(self):
        # save to output file
        with open(self.output_path, "w") as f:
            f.write("\n".join(self._lines) + "\n")
        print(f"[VMWriter] Written {len(self._lines)} VM lines → {self.output_path}")

    # translate segment names

    @staticmethod
    def kind_to_segment(kind: str) -> str:
        # map symbol kind to segment
        return {
            "static":   "static",
            "field":    "this",
            "argument": "argument",
            "local":    "local",
        }[kind]