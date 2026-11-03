"""Minimal DXF (R12) writer: board outline, all drilled holes, and reference marks.

Coordinates are board-local millimetres, origin = board bottom-left corner, +Y up
(the usual CAD convention). Layers: OUTLINE, HOLES_NPTH, HOLES_PTH, MOUNT_M2, KEY_CENTERS,
USB_C, ENCODER.
"""
import math
import pcbnew
import gen_pcb, design

W, H, OX, OY = gen_pcb.W, gen_pcb.H, gen_pcb.OX, gen_pcb.OY


def _b(x_page_mm, y_page_mm):
    return x_page_mm - OX, H - (y_page_mm - OY)


class Dxf:
    def __init__(self):
        self.e = []

    def line(self, l, a, b):
        self.e += ["0", "LINE", "8", l, "10", f"{a[0]:.4f}", "20", f"{a[1]:.4f}", "11", f"{b[0]:.4f}", "21", f"{b[1]:.4f}"]

    def circle(self, l, c, r):
        self.e += ["0", "CIRCLE", "8", l, "10", f"{c[0]:.4f}", "20", f"{c[1]:.4f}", "40", f"{r:.4f}"]

    def arc(self, l, c, r, a0, a1):
        self.e += ["0", "ARC", "8", l, "10", f"{c[0]:.4f}", "20", f"{c[1]:.4f}", "40", f"{r:.4f}", "50", f"{a0:.4f}", "51", f"{a1:.4f}"]

    def text(self, l, p, h, s):
        self.e += ["0", "TEXT", "8", l, "10", f"{p[0]:.4f}", "20", f"{p[1]:.4f}", "40", f"{h}", "1", s]

    def save(self, path):
        hdr = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
        with open(path, "w") as f:
            f.write("\n".join(hdr + self.e + ["0", "ENDSEC", "0", "EOF"]) + "\n")


def write(board, path):
    d = Dxf()
    # outline straight from Edge.Cuts
    for s in board.GetDrawings():
        if s.GetLayer() != pcbnew.Edge_Cuts:
            continue
        sh = s.GetShape()
        if sh == pcbnew.SHAPE_T_SEGMENT:
            a, b = s.GetStart(), s.GetEnd()
            d.line("OUTLINE", _b(pcbnew.ToMM(a.x), pcbnew.ToMM(a.y)), _b(pcbnew.ToMM(b.x), pcbnew.ToMM(b.y)))
        elif sh == pcbnew.SHAPE_T_ARC:
            c = s.GetCenter(); r = pcbnew.ToMM(s.GetRadius())
            st, en = s.GetStart(), s.GetEnd()
            cc = _b(pcbnew.ToMM(c.x), pcbnew.ToMM(c.y))
            def ang(p):
                q = _b(pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)); return math.degrees(math.atan2(q[1] - cc[1], q[0] - cc[0]))
            a0, a1 = ang(st), ang(en)
            # KiCad arcs run clockwise on screen (y down) == counter-clockwise in y-up; DXF arcs are CCW
            if (a1 - a0) % 360 > 180:
                a0, a1 = a1, a0
            d.arc("OUTLINE", cc, r, a0, a1)
    # holes
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetDrillSize().x <= 0:
                continue
            pos = p.GetPosition(); c = _b(pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))
            r = pcbnew.ToMM(p.GetDrillSize().x) / 2
            ref = fp.GetReference()
            layer = "MOUNT_M2" if ref.startswith("H") else ("HOLES_NPTH" if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else "HOLES_PTH")
            d.circle(layer, c, r)
    # key centres (crosses) and switch cutout reference (14 x 14 mm plate hole)
    for r in range(design.ROWS):
        for c in range(design.COLS):
            x, y = gen_pcb.key_center(r * design.COLS + c + 1)
            q = (x, H - y)
            d.line("KEY_CENTERS", (q[0] - 1, q[1]), (q[0] + 1, q[1])); d.line("KEY_CENTERS", (q[0], q[1] - 1), (q[0], q[1] + 1))
            for (ax, ay), (bx, by) in [((-7, -7), (7, -7)), ((7, -7), (7, 7)), ((7, 7), (-7, 7)), ((-7, 7), (-7, -7))]:
                d.line("KEY_CENTERS", (q[0] + ax, q[1] + ay), (q[0] + bx, q[1] + by))
    # USB-C mouth and encoder shaft
    jx, _, _ = gen_pcb.PLACE["J1"]
    d.line("USB_C", (jx - 4.47, H), (jx + 4.47, H)); d.text("USB_C", (jx - 4.47, H - 3), 1.5, "USB-C mouth 8.94 wide, top edge")
    ex, ey = 226.0, 12.0
    d.circle("ENCODER", (ex, H - ey), 3.0); d.text("ENCODER", (ex - 6, H - ey - 9), 1.5, "EC11 shaft 6mm")
    d.save(path)
