"""Minimal Paradox script parser/serializer used by build_mod.py.

A parsed block is a list of (key, op, value) tuples, where value is either a
string token or another block (list). Order and duplicate keys are preserved.
"""
import re

_TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|[{}]|[<>!]?=|[<>]|[^\s{}=<>#"]+|#[^\n]*')


def tokenize(text):
    for m in _TOKEN.finditer(text):
        tok = m.group(0)
        if tok.startswith('#'):
            continue
        yield tok


def parse(text):
    if text.startswith('\ufeff'):
        text = text[1:]
    toks = list(tokenize(text))
    pos = 0

    def block():
        nonlocal pos
        out = []
        while pos < len(toks):
            t = toks[pos]
            if t == '}':
                pos += 1
                return out
            if t == '{':  # anonymous block
                pos += 1
                out.append((None, None, block()))
                continue
            # key [op value] or bare value (inside arrays)
            if pos + 1 < len(toks) and toks[pos + 1] in ('=', '<', '>', '<=', '>=', '!='):
                key, op = t, toks[pos + 1]
                pos += 2
                if pos < len(toks) and toks[pos] == '{':
                    pos += 1
                    out.append((key, op, block()))
                else:
                    out.append((key, op, toks[pos] if pos < len(toks) else ''))
                    pos += 1
            else:
                out.append((None, None, t))
                pos += 1
        return out

    return block()


def get(blk, key, default=None):
    for k, _, v in blk:
        if k == key:
            return v
    return default


def get_all(blk, key):
    return [v for k, _, v in blk if k == key]


def values(blk):
    """Bare values of an array block."""
    return [v for k, _, v in blk if k is None and isinstance(v, str)]


def dump(blk, indent=0):
    pad = '\t' * indent
    lines = []
    for k, op, v in blk:
        if isinstance(v, list):
            head = f'{pad}{k} {op} {{' if k is not None else f'{pad}{{'
            if v and all(kk is None and isinstance(vv, str) for kk, _, vv in v):
                lines.append(head + ' ' + ' '.join(vv for _, _, vv in v) + ' }')
            else:
                lines.append(head)
                lines.append(dump(v, indent + 1))
                lines.append(f'{pad}}}')
        else:
            lines.append(f'{pad}{k} {op} {v}' if k is not None else f'{pad}{v}')
    return '\n'.join(l for l in lines if l != '')
