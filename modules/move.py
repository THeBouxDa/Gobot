class Move():
    def __init__(self, data: dict[str, str]) -> None:
        self.data = data
    
    def __repr__(self) -> str:
        return self.format_self(depth=0)

    def format_self(self, depth: int):
        indent: str = "\t" * depth
        in_indent: str = "\t" * (depth + 1)
        output = f'{indent}{{\n'
        
        for key, value in self.data.items():
            output += f'{in_indent}"{key}": "{value}"\n'
        
        return f'{output}{indent}}}'
    
    def get_prop(self, prop: str) -> str:
        return self.data.get(prop, "")
    
    # def get_useful_data(self) -> list[str]:
    #     move.get_prop('category'), move.get_prop('name'), move.get_prop('input'),
    #     move.get_prop('startup'), move.get_prop('active'), move.get_prop('recovery'),
    #     move.get_prop('damage'), move.get_prop('guard'), move.get_prop('invuln'),
    #     move.get_prop('images'), move.get_prop('hitboxes'), move.get_prop('onBlock'),
    #     move.get_prop('onHit')