class SymbolTable:
    # tracks variables in two scopes

    def __init__(self):
        # maps name to type kind index
        self.class_table = {}
        self.sub_table   = {}
        self._counters   = {"static": 0, "field": 0, "argument": 0, "local": 0}

    # scope management

    def start_subroutine(self):
        # reset local and argument scope
        self.sub_table = {}
        self._counters["argument"] = 0
        self._counters["local"]    = 0

    # define new variables

    def define(self, name: str, typ: str, kind: str):
        # add to appropriate scope
        idx = self._counters[kind]
        self._counters[kind] += 1

        if kind in ("static", "field"):
            self.class_table[name] = (typ, kind, idx)
        else:
            self.sub_table[name] = (typ, kind, idx)

    # lookup helpers

    def _lookup(self, name: str) -> tuple | None:
        # find variable in scopes
        return self.sub_table.get(name) or self.class_table.get(name)

    def type_of(self, name: str) -> str:
        entry = self._lookup(name)
        return entry[0] if entry else None

    def kind_of(self, name: str) -> str:
        # get variable kind
        entry = self._lookup(name)
        return entry[1] if entry else None

    def index_of(self, name: str) -> int:
        entry = self._lookup(name)
        return entry[2] if entry else None

    def contains(self, name: str) -> bool:
        return self._lookup(name) is not None

    def var_count(self, kind: str) -> int:
        # count variables of kind
        return self._counters[kind]

    # debug printing

    def dump(self) -> str:
        lines = ["=== Class Scope ==="]
        for name, (t, k, i) in self.class_table.items():
            lines.append(f"  {name:20s}  type={t:10s}  kind={k:10s}  index={i}")
        lines.append("=== Subroutine Scope ===")
        for name, (t, k, i) in self.sub_table.items():
            lines.append(f"  {name:20s}  type={t:10s}  kind={k:10s}  index={i}")
        return "\n".join(lines)