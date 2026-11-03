import copy, glob, os
from sexp import parse, find, first, Sym

LIBDIR = "/usr/share/kicad/symbols"
_cache = {}

def lib(name):
    if name not in _cache:
        _cache[name] = parse(open(os.path.join(LIBDIR, name + ".kicad_sym")).read())
    return _cache[name]

def get_symbol(lib_id):
    """Return a flattened symbol node named lib_id ('Lib:Name')."""
    libname, name = lib_id.split(":")
    L = lib(libname)
    syms = {s[1]: s for s in find(L, "symbol")}
    s = copy.deepcopy(syms[name])
    ext = first(s, "extends")
    if ext:
        parent = copy.deepcopy(get_symbol(f"{libname}:{ext[1]}"))
        pname = parent[1].split(":")[1]
        # child properties override parent's
        cprops = {p[1]: p for p in find(s, "property")}
        newp = [Sym("symbol"), name]
        for e in parent[2:]:
            if isinstance(e, list) and e[0] == "property" and e[1] in cprops:
                newp.append(cprops.pop(e[1]))
            elif isinstance(e, list) and e[0] == "symbol":
                e[1] = e[1].replace(pname, name, 1)
                newp.append(e)
            else:
                newp.append(e)
        for p in cprops.values():
            newp.append(p)
        s = newp
    s[1] = lib_id
    return s

def pins(sym):
    """[(number, name, x, y, angle, length, etype)] in symbol coords (y up)."""
    out = []
    def walk(n):
        for e in n:
            if isinstance(e, list):
                if e[0] == "pin":
                    at = first(e, "at"); ln = first(e, "length")
                    nm = first(e, "name")[1]; num = first(e, "number")[1]
                    out.append((num, nm, float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0, float(ln[1]), str(e[1])))
                else:
                    walk(e)
    walk(sym)
    return out
