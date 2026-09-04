from configs.config import broken_chars



def indent_size(string: str, size: int) -> str:
    return string.replace("\t", " " * size)

def sanitize(string: str) -> str:
    return str(string.replace(" ", "_")).translate(
        str.maketrans("", "", broken_chars)
    )