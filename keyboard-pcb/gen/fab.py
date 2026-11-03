"""Fab outputs for JLCPCB-style ordering (files only; nothing is uploaded anywhere).

Writes into ../fab/: gerbers + drill (zipped), bom-jlc.csv, cpl-jlc.csv, hand-solder.csv,
renders into ../renders/, and DXF outline/holes into ../mech/.
"""
import csv, os, subprocess, shutil, zipfile, collections
import pcbnew

PRJ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PCB = os.path.join(PRJ, "ssp-wedge-kb.kicad_pcb")
FAB = os.path.join(PRJ, "fab"); REN = os.path.join(PRJ, "renders"); MECH = os.path.join(PRJ, "mech")
for d in (FAB, REN, MECH):
    os.makedirs(d, exist_ok=True)
import gen_pcb
OX, OY, W, H = gen_pcb.OX, gen_pcb.OY, gen_pcb.W, gen_pcb.H


def run(*a):
    print("+", " ".join(a)); subprocess.run(a, check=True)


# ---- gerbers + drill ----
g = os.path.join(FAB, "gerbers"); shutil.rmtree(g, ignore_errors=True); os.makedirs(g)
layers = "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"
run("kicad-cli", "pcb", "export", "gerbers", "-o", g + "/", "-l", layers, "--subtract-soldermask", "--use-drill-file-origin", PCB)
run("kicad-cli", "pcb", "export", "drill", "-o", g + "/", "--format", "excellon", "--excellon-separate-th", "--drill-origin", "plot",
    "--generate-map", "--map-format", "gerberx2", "-u", "mm", PCB)
z = os.path.join(FAB, "ssp-wedge-kb-gerbers.zip")
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(os.listdir(g)):
        zf.write(os.path.join(g, f), f)

# ---- BOM / CPL ----
b = pcbnew.LoadBoard(PCB)
groups = collections.OrderedDict(); cpl = []; hand = []; dnp = []
DNP_WHY = {"J2": "DNP - DO NOT FIT: a fitted SWD header collides with the case plate (Wedge case v1.1). Use BOOT/RESET via the plate poke holes; pogo onto the pads only if SWD is ever needed."}
for f in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    ref = f.GetReference()
    if f.IsDNP():
        dnp.append((ref, f.GetValue(), str(f.GetFPID().GetLibItemName()), "top", "DNP",
                    DNP_WHY.get(ref, "DNP - DO NOT FIT")))
        continue
    if f.IsDNP() or f.IsExcludedFromBOM() or ref.startswith("H"):
        continue
    val = f.GetValue(); fpn = str(f.GetFPID().GetLibItemName())
    lcsc = f.GetFieldText("LCSC") if f.HasField("LCSC") else ""
    # hot-swap sockets: footprint sits on F.Cu (switch side) but its SMD pads are on B.Cu
    socket = "Hotswap" in fpn
    bottom = f.GetLayer() == pcbnew.B_Cu or socket
    tht = any(p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for p in f.Pads()) and not socket
    if bottom or ref == "ENC1":
        hand.append((ref, "Kailh MX hot-swap socket (" + lcsc + ")" if socket else val, fpn,
                     "bottom" if bottom else "top", "THT" if tht else "SMD"))
        continue
    groups.setdefault((val, fpn, lcsc), []).append(ref)
    p = f.GetPosition()
    cpl.append((ref, f"{pcbnew.ToMM(p.x) - OX:.3f}mm", f"{H - (pcbnew.ToMM(p.y) - OY):.3f}mm", "Top",
                f"{f.GetOrientationDegrees() % 360:.1f}"))

with open(os.path.join(FAB, "bom-jlc.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (val, fpn, lcsc), refs in groups.items():
        w.writerow([val, ",".join(sorted(refs, key=lambda r: (r.rstrip("0123456789"), int("0" + r.lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))))), fpn, lcsc])
with open(os.path.join(FAB, "cpl-jlc.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    w.writerows(cpl)
with open(os.path.join(FAB, "hand-solder.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["Designator", "Value", "Footprint", "Side", "Type", "Note"])
    w.writerows([h + ("",) for h in hand])
    w.writerows(dnp)          # listed so nobody fits them; Type = DNP
# DNP parts are kept OUT of bom-jlc.csv / cpl-jlc.csv on purpose: JLC places only what those files list.
with open(os.path.join(FAB, "dnp.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["Designator", "Value", "Footprint", "Side", "Type", "Note"])
    w.writerows(dnp)
print("BOM lines", len(groups), "CPL parts", len(cpl), "hand-solder", len(hand), "DNP", [d[0] for d in dnp])

# ---- renders ----
for side in ("top", "bottom"):
    run("kicad-cli", "pcb", "render", "-o", os.path.join(REN, f"ssp-wedge-kb-{side}.png"), "--side", side,
        "--width", "2400", "--height", "1100", "--zoom", "2.1", "--background", "opaque", "--quality", "high", PCB)

# ---- DXF (outline + holes + reference marks) for the case designer ----
import math, gen_mech
gen_mech.write(b, os.path.join(MECH, "ssp-wedge-kb-outline.dxf"))
