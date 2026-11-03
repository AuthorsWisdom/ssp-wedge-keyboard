"""Tiny S-expression reader/writer for KiCad files (our own code, MIT)."""
import re

class Sym(str):
    """Bare (unquoted) atom."""

_tok = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))', re.S)

def parse(text):
    stack = [[]]
    pos = 0
    n = len(text)
    while pos < n:
        m = _tok.match(text, pos)
        if not m:
            if text[pos:].strip() == "":
                break
            raise ValueError(f"bad token at {pos}")
        pos = m.end()
        if m.group(1):
            stack.append([])
        elif m.group(2):
            x = stack.pop()
            stack[-1].append(x)
        elif m.group(3) is not None:
            stack[-1].append(m.group(3).replace('\\"', '"').replace("\\\\", "\\"))
        elif m.group(4) is not None:
            stack[-1].append(Sym(m.group(4)))
    return stack[0][0]

def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'

def dump(x, ind=0):
    if isinstance(x, list):
        if not x:
            return "()"
        simple = all(not isinstance(e, list) for e in x)
        if simple:
            return "(" + " ".join(dump(e) for e in x) + ")"
        out = "(" + dump(x[0])
        for e in x[1:]:
            if isinstance(e, list):
                out += "\n" + "\t" * (ind + 1) + dump(e, ind + 1)
            else:
                out += " " + dump(e)
        return out + "\n" + "\t" * ind + ")"
    if isinstance(x, Sym):
        return str(x)
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, (int, float)):
        s = f"{x:.4f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return q(x)

def find(node, key):
    return [e for e in node if isinstance(e, list) and e and e[0] == key]

def first(node, key):
    r = find(node, key)
    return r[0] if r else None
