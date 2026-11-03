"""Export DSN -> Freerouting (GPL tool, run as a separate program) -> import SES -> GND pours."""
import os, subprocess, sys, pcbnew
import gen_pcb

PRJ = gen_pcb.PRJ
PCB = os.path.join(PRJ, "ssp-wedge-kb.kicad_pcb")
DSN = os.path.join(PRJ, "route", "ssp-wedge-kb.dsn")
SES = os.path.join(PRJ, "route", "ssp-wedge-kb.ses")
FR = os.environ.get("FREEROUTING", "freerouting")
os.makedirs(os.path.dirname(DSN), exist_ok=True)

step = sys.argv[1] if len(sys.argv) > 1 else "all"
if step in ("all", "dsn"):
    b = gen_pcb.build(PCB)
    b = pcbnew.LoadBoard(PCB)
    assert pcbnew.ExportSpecctraDSN(b, DSN)
    print("DSN written")
if step in ("all", "route"):
    passes = os.environ.get("PASSES", "40")
    subprocess.run([FR, "-de", DSN, "-do", SES, "-mp", passes, "-mt", "6", "--gui.enabled=false"], check=True)
if step in ("all", "ses"):
    b = pcbnew.LoadBoard(PCB)
    assert pcbnew.ImportSpecctraSES(b, SES)
    b.GetDesignSettings().SetAuxOrigin(gen_pcb.mm(0, gen_pcb.H))
    # Freerouting necks a few pad-entry stubs down to 0.12 mm; JLC 2-layer minimum is 0.127 mm
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_TRACE_T and t.GetWidth() < pcbnew.FromMM(0.15):
            t.SetWidth(pcbnew.FromMM(0.15))
    gen_pcb.add_zones(b)
    pcbnew.SaveBoard(PCB, b)
    print("routed board saved")
if step == "pass2":
    # second Freerouting run seeded with the current routing (and GND pours as planes)
    dsn2, ses2 = DSN.replace(".dsn", "-pass2.dsn"), SES.replace(".ses", "-pass2.ses")
    b = pcbnew.LoadBoard(PCB)
    assert pcbnew.ExportSpecctraDSN(b, dsn2)
    subprocess.run([FR, "-de", dsn2, "-do", ses2, "-mp", os.environ.get("PASSES", "30"), "-mt", "6",
                    "--gui.enabled=false"], check=True)
    b = pcbnew.LoadBoard(PCB)
    assert pcbnew.ImportSpecctraSES(b, ses2)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(PCB, b)
    print("pass2 board saved")
