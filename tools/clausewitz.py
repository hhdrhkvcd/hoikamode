"""Small, strict Clausewitz text reader used by the importer and offline checks.

Unlike a dict, Block preserves repeated keys (cores, focuses, if/else, etc.).
It does not execute game scripts or claim to replace the HOI4 engine validator.
No third-party packages are needed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


class ParseError(ValueError):
    pass


@dataclass
class Entry:
    key: str
    value: str | Block | Tagged
    op: str = "="


@dataclass
class Tagged:
    tag: str
    block: Block


@dataclass
class Block:
    items: list[Entry | str] = field(default_factory=list)

    def entries(self, key: str | None = None) -> list[Entry]:
        return [
            i
            for i in self.items
            if isinstance(i, Entry) and (key is None or i.key == key)
        ]

    def values(self, key: str) -> list[str | Block | Tagged]:
        return [i.value for i in self.entries(key)]

    def get(self, key: str, default=None):
        found = self.values(key)
        return found[-1] if found else default

    def scalar(self, key: str, default=None):
        value = self.get(key, default)
        if isinstance(value, str):
            return unquote(value)
        if value is None:
            return default
        raise ParseError(f"Expected scalar {key}, got {type(value).__name__}")

    def block(self, key: str) -> Block:
        value = self.get(key)
        if not isinstance(value, Block):
            raise ParseError(f"Expected block {key}")
        return value

    def atoms(self) -> list[str]:
        if any(not isinstance(i, str) for i in self.items):
            raise ParseError("Expected a list of scalar values")
        return [unquote(i) for i in self.items]

    def set(self, key: str, value: str | Block | Tagged):
        self.remove(key)
        self.items.append(Entry(key, value))

    def add(self, key: str, value: str | Block | Tagged):
        self.items.append(Entry(key, value))

    def remove(self, key: str):
        self.items[:] = [
            i for i in self.items if not isinstance(i, Entry) or i.key != key
        ]


TOKEN = re.compile(
    r'\s+|\#[^\r\n]*|"(?:\\.|[^"\\])*"|[{}]|(?:>=|<=|!=|=|>|<)|[^\s{}=<>!#"]+'
)
OPS = {"=", ">", "<", ">=", "<=", "!="}


def unquote(value: str) -> str:
    return value[1:-1] if value.startswith('"') and value.endswith('"') else value


def quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse(text: str, source: str = "<text>") -> Block:
    tokens: list[str] = []
    pos = 0
    for match in TOKEN.finditer(text.lstrip("\ufeff")):
        if match.start() != pos:
            raise ParseError(f"{source}: invalid text at offset {pos}")
        pos = match.end()
        token = match.group()
        if not token.isspace() and not token.startswith("#"):
            tokens.append(token)
    if pos != len(text.lstrip("\ufeff")):
        raise ParseError(f"{source}: invalid text at offset {pos}")
    index = 0

    def value():
        nonlocal index
        if index >= len(tokens):
            raise ParseError(f"{source}: unexpected end of file")
        token = tokens[index]
        if token == "{":
            index += 1
            return body(True)
        if token == "}" or token in OPS:
            raise ParseError(f"{source}: unexpected token {token!r}")
        index += 1
        if index < len(tokens) and tokens[index] == "{":
            index += 1
            return Tagged(token, body(True))
        return token

    def body(nested: bool) -> Block:
        nonlocal index
        result = Block()
        while index < len(tokens):
            token = tokens[index]
            if token == "}":
                if not nested:
                    raise ParseError(f"{source}: unexpected closing brace")
                index += 1
                return result
            if token == "{" or token in OPS:
                raise ParseError(f"{source}: unexpected token {token!r}")
            index += 1
            if index < len(tokens) and tokens[index] in OPS:
                op = tokens[index]
                index += 1
                result.items.append(Entry(token, value(), op))
            else:
                result.items.append(token)
        if nested:
            raise ParseError(f"{source}: unclosed block")
        return result

    return body(False)


def read(path: str | Path, *, legacy: bool = False) -> Block:
    path = Path(path)
    data = path.read_bytes()
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        if not legacy:
            raise
        text = data.decode("cp1252")
    return parse(text, str(path))


def dumps(block: Block, indent: int = 0) -> str:
    def render(value, level):
        if isinstance(value, Tagged):
            return value.tag + " " + render(value.block, level)
        if isinstance(value, str):
            return value
        if not value.items:
            return "{ }"
        if all(isinstance(i, str) for i in value.items):
            return "{ " + " ".join(value.items) + " }"
        return "{\n" + dumps(value, level + 1) + "    " * level + "}"

    lines = []
    for item in block.items:
        prefix = "    " * indent
        if isinstance(item, Entry):
            lines.append(f"{prefix}{item.key} {item.op} {render(item.value, indent)}\n")
        else:
            lines.append(f"{prefix}{item}\n")
    return "".join(lines)


def write(path: str | Path, block: Block, header: str = ""):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + dumps(block), encoding="utf-8")


def walk(block: Block):
    """Yield every assignment recursively, without flattening duplicate keys."""
    for entry in block.entries():
        yield entry
        if isinstance(entry.value, Block):
            yield from walk(entry.value)
        elif isinstance(entry.value, Tagged):
            yield from walk(entry.value.block)
