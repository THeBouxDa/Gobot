class Move:
    def __init__(self, data: dict[str, str]) -> None:
        self.data = data

    def __repr__(self) -> str:
        return self.format_self(depth=0)

    def format_self(self, depth: int) -> str:
        indent: str = "\t" * depth
        in_indent: str = "\t" * (depth + 1)
        output = f"{indent}{{\n"

        for key, value in self.data.items():
            output += f'{in_indent}"{key}": "{value}"\n'

        return f"{output}{indent}}}"

    def get_prop(self, prop: str) -> str:
        return self.data.get(prop, "")
