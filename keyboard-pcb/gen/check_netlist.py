"""Cross-check the KiCad-exported netlist against design.py."""
import os, sys, re
sys.path.insert(0, os.path.dirname(__file__))
import design, sexp
net = sexp.parse(open(os.path.join(os.path.dirname(__file__), "..", "ssp-wedge-kb.net")).read())
got = {}
def walk(n):
    if isinstance(n, list) and n and str(n[0]) == "net":
        name = next(str(x[1]) for x in n if isinstance(x, list) and str(x[0]) == "name")
        for x in n:
            if isinstance(x, list) and str(x[0]) == "node":
                d = {str(y[0]): str(y[1]) for y in x[1:] if isinstance(y, list)}
                got[(d["ref"], d["pin"])] = name.lstrip("/")
    elif isinstance(n, list):
        for x in n: walk(x)
walk(net)
bad = 0
for p in design.build():
    for pin, n in p["pins"].items():
        if n and p["ref"] != "ENC1" or (p["ref"] == "ENC1" and pin != "MP" and n):
            g = got.get((p["ref"], pin))
            if g != n:
                bad += 1; print("MISMATCH", p["ref"], pin, n, g)
print("mismatches:", bad)
