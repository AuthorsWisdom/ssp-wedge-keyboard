"""Build ssp-wedge-kb.kicad_pcb (placement, nets, outline, holes) from design.py."""
import pcbnew, os
import design

W, H = 240.0, 102.0
OX, OY = 20.0, 20.0           # board origin offset on the page
GRID_X0 = (W - design.COLS * design.PITCH) / 2
GRID_Y0 = 23.0
FPDIR = "/usr/share/kicad/footprints"
HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(HERE)

def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(OX + x), pcbnew.FromMM(OY + y))

def key_center(n):
    r, c = divmod(n - 1, design.COLS)
    return (GRID_X0 + design.PITCH * (c + 0.5), GRID_Y0 + design.PITCH * (r + 0.5))

# (x, y, rotation_deg) for non-matrix parts, top side
PLACE = {
    "J1": (16.0, 3.65, 180), "R5": (8.5, 10.0, 90), "R6": (23.5, 10.0, 90),
    "U3": (16.0, 13.5, 0), "R7": (22.5, 15.0, 0), "R8": (22.5, 17.0, 0),
    "U4": (31.0, 10.0, 0), "C16": (26.5, 4.5, 90), "C17": (36.5, 5.0, 90),
    "U2": (45.0, 12.0, 90), "C13": (45.0, 6.0, 0), "R1": (40.5, 17.5, 90), "R2": (49.5, 18.0, 0),
    "U1": (62.0, 12.0, 90),
    "C1": (57.0, 6.5, 0), "C2": (62.0, 5.8, 0), "C3": (67.0, 6.5, 0), "C4": (57.0, 17.5, 0),
    "C5": (62.0, 18.2, 0), "C6": (67.0, 17.5, 0), "C7": (55.5, 10.0, 90), "C8": (55.5, 14.0, 90),
    "C9": (68.5, 9.0, 90), "C10": (68.5, 15.0, 90), "C11": (70.0, 12.0, 90), "C12": (59.0, 20.0, 0),
    "Y1": (75.0, 12.0, 0), "R4": (72.5, 17.0, 90), "C14": (75.0, 8.5, 0), "C15": (75.0, 15.5, 0),
    "SW49": (86.0, 8.0, 0), "SW50": (86.0, 17.0, 0), "R3": (80.0, 19.5, 0),
    "J2": (96.0, 9.5, 0),
    "ENC1": (226.0 - 7.5, 12.0 - 2.5, 0), "D49": (213.5, 12.0, 90),
}
HOLES = [(3.5, 3.5), (W - 3.5, 3.5), (150.0, 6.0),
         (GRID_X0 + 2 * design.PITCH, GRID_Y0 + 2 * design.PITCH),
         (GRID_X0 + 6 * design.PITCH, GRID_Y0 + 2 * design.PITCH),
         (GRID_X0 + 10 * design.PITCH, GRID_Y0 + 2 * design.PITCH),
         (GRID_X0 + 1 * design.PITCH, GRID_Y0 + 3 * design.PITCH),
         (GRID_X0 + 11 * design.PITCH, GRID_Y0 + 3 * design.PITCH)]

def load_fp(fpid):
    lib, name = fpid.split(":")
    path = os.path.join(PRJ, "lib", lib + ".pretty") if lib == "SSP_Wedge" else os.path.join(FPDIR, lib + ".pretty")
    f = pcbnew.FootprintLoad(path, name)
    f.SetFPID(pcbnew.LIB_ID(lib, name))
    return f

def build(out):
    parts = design.build()
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(2)
    ds = b.GetDesignSettings()
    ds.SetAuxOrigin(mm(0, H))  # fab/place origin = board bottom-left
    ds.m_TrackMinWidth = pcbnew.FromMM(0.15)
    ds.m_MinClearance = pcbnew.FromMM(0.15)
    ds.m_ViasMinSize = pcbnew.FromMM(0.5)
    ds.m_MinThroughDrill = pcbnew.FromMM(0.3)
    ds.m_HoleClearance = pcbnew.FromMM(0.25)
    ds.m_CopperEdgeClearance = pcbnew.FromMM(0.3)
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(pcbnew.FromMM(0.15)); nc.SetTrackWidth(pcbnew.FromMM(0.2))
    nc.SetViaDiameter(pcbnew.FromMM(0.5)); nc.SetViaDrill(pcbnew.FromMM(0.3))

    try:
        ns = ds.m_NetSettings
        pw = pcbnew.NETCLASS("Power")
        pw.SetClearance(pcbnew.FromMM(0.15)); pw.SetTrackWidth(pcbnew.FromMM(0.25))  # must fan into 0.4 mm-pitch QFN pads
        pw.SetViaDiameter(pcbnew.FromMM(0.6)); pw.SetViaDrill(pcbnew.FromMM(0.3))
        ns.SetNetclass("Power", pw)
        for n in ("VBUS", "GND"):
            ns.SetNetclassPatternAssignment(n, "Power")
        # +3V3/+1V1 draw < 100 mA; 0.2 mm lets them escape the 0.4 mm-pitch RP2040 pads
        rl = pcbnew.NETCLASS("Rail")
        rl.SetClearance(pcbnew.FromMM(0.15)); rl.SetTrackWidth(pcbnew.FromMM(0.2))
        rl.SetViaDiameter(pcbnew.FromMM(0.6)); rl.SetViaDrill(pcbnew.FromMM(0.3))
        ns.SetNetclass("Rail", rl)
        for n in ("+3V3", "+1V1"):
            ns.SetNetclassPatternAssignment(n, "Rail")
    except Exception as e:
        print("netclass setup skipped:", e)
    nets = {}
    def net(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(b, name); b.Add(n); nets[name] = n
        return nets[name]

    hole_i = 0
    for p in parts:
        f = load_fp(p["fp"])
        f.SetReference(p["ref"]); f.SetValue(p["value"])
        if p["lcsc"]:
            f.SetField("LCSC", p["lcsc"])
            fld = f.GetFieldByName("LCSC")
            if fld: fld.SetVisible(False)
        b.Add(f)
        ref = p["ref"]
        if ref.startswith("SW") and p["value"] == "MX":
            x, y = key_center(int(ref[2:])); rot = 0
        elif ref.startswith("D") and ref[1:].isdigit() and int(ref[1:]) <= 48:
            x, y = key_center(int(ref[1:])); y += design.PITCH / 2; rot = 0
        elif ref.startswith("H"):
            x, y = HOLES[hole_i]; hole_i += 1; rot = 0
        else:
            x, y, rot = PLACE[ref]
        f.SetPosition(mm(x, y))
        if rot:
            f.SetOrientationDegrees(rot)
        if p.get("dnp"):
            f.SetDNP(True); f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True)
        if not p.get("bom", True):
            f.SetExcludedFromBOM(True)
        if ref.startswith("H"):
            f.SetExcludedFromPosFiles(True)
        for pad in f.Pads():
            num = pad.GetNumber()
            nn = p["pins"].get(num)
            if num == "MP" and ref == "ENC1":
                nn = "GND"
            if nn:
                pad.SetNet(net(nn))
        f.Reference().SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
        f.Reference().SetTextThickness(pcbnew.FromMM(0.12))
        if ref.startswith(("SW", "D", "C", "R", "H")) and not ref.startswith(("SW49", "SW50")):
            f.Reference().SetVisible(False)

    # outline with 1 mm corner radius
    r = 1.0
    def seg(a, c):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(mm(*a)); s.SetEnd(mm(*c)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(pcbnew.FromMM(0.1)); b.Add(s)
    def arc(cx, cy, start):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(mm(cx, cy)); s.SetStart(mm(*start)); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(pcbnew.FromMM(0.1)); b.Add(s)
    seg((r, 0), (W - r, 0)); seg((W, r), (W, H - r)); seg((W - r, H), (r, H)); seg((0, H - r), (0, r))
    arc(W - r, r, (W - r, 0)); arc(W - r, H - r, (W, H - r)); arc(r, H - r, (r, H)); arc(r, r, (0, r))

    # silk title
    t = pcbnew.PCB_TEXT(b); t.SetText("SEVEN SWORDS WEDGE  KB-P1  2026-11-03")
    t.SetPosition(mm(150, 16)); t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.5), pcbnew.FromMM(1.5))); t.SetTextThickness(pcbnew.FromMM(0.2)); b.Add(t)
    t2 = pcbnew.PCB_TEXT(b); t2.SetText("RP2040 core after Raspberry Pi Minimal RP2040 (MIT)")
    t2.SetPosition(mm(150, 19.5)); t2.SetLayer(pcbnew.F_SilkS)
    t2.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8))); t2.SetTextThickness(pcbnew.FromMM(0.12)); b.Add(t2)

    add_branding(b)
    b.SetFileName(out)
    pcbnew.SaveBoard(out, b)
    return b

LICENSE_SILK = "CERN-OHL-P-2.0  (c) 2026 Seven Swords Productions"

def add_branding(b):
    """Licence line on F.Silk (free strip between the title and the key grid) + PCB title block."""
    t3 = pcbnew.PCB_TEXT(b); t3.SetText(LICENSE_SILK)
    t3.SetPosition(mm(150, 21.7)); t3.SetLayer(pcbnew.F_SilkS)
    t3.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.0), pcbnew.FromMM(1.0))); t3.SetTextThickness(pcbnew.FromMM(0.15)); b.Add(t3)
    tb = b.GetTitleBlock()
    tb.SetTitle("Seven Swords Wedge keyboard PCB (KB-P1)"); tb.SetRevision("P1"); tb.SetDate("2026-11-03")
    tb.SetCompany("Seven Swords Productions")
    tb.SetComment(0, "SPDX-License-Identifier: CERN-OHL-P-2.0")
    tb.SetComment(1, "RP2040 core after Raspberry Pi Minimal RP2040 reference design (MIT), see NOTICE.md")
    tb.SetComment(2, "J2 (SWD) DNP: a fitted header collides with the case plate")
    b.SetTitleBlock(tb)

def add_zones(b):
    gnd = b.FindNet("GND")
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(gnd)
        o = z.Outline(); o.NewOutline()
        for x, y in [(0.5, 0.5), (W - 0.5, 0.5), (W - 0.5, H - 0.5), (0.5, H - 0.5)]:
            o.Append(pcbnew.FromMM(OX + x), pcbnew.FromMM(OY + y))
        z.SetLocalClearance(pcbnew.FromMM(0.25))
        z.SetMinThickness(pcbnew.FromMM(0.2))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        b.Add(z)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())

if __name__ == "__main__":
    import sys
    out = os.path.join(PRJ, "ssp-wedge-kb.kicad_pcb")
    b = build(out)
    print("saved", out, "footprints", len(b.GetFootprints()), "nets", b.GetNetCount())
