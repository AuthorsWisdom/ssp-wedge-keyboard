# Dims note for the case: Wedge keyboard PCB rev A

Companion to `mech/ssp-wedge-kb-outline.dxf` (DXF R12, mm). **Origin is the board's bottom-left corner, +X right, +Y up**, looking at the top (switch) side. In this frame the board's "top edge" (y = 102) is the edge facing the screen/hinge.

## Board
- 240.0 × 102.0 mm, 1.6 mm FR4, R1.0 corners.
- Switches go on the **top** side, and the plate sits between the switches and the PCB. MX standard is 5.0 mm from PCB top to plate top, with a 1.5 mm plate.
- Bottom side: 48 Kailh hot-swap sockets, about 1.8 mm below the PCB, at every key. Leave ≥ 3 mm of clearance under the PCB, or a pocket.
- Top-side parts under the plate (tallest is the USB-C at ~3.2 mm) are all < 3.5 mm, so they clear a standard plate.

## Holes (DXF layers HOLES_NPTH / HOLES_PTH / MOUNT_M2)
M2 mounting holes are Ø2.2 mm NPTH (no copper, keep-out Ø5 mm around each). Use M2 standoffs or heat-set inserts.

| # | x | y |
|---|---|---|
| H1 | 3.50 | 98.50 |
| H2 | 236.50 | 98.50 |
| H3 | 150.00 | 96.00 |
| H4 | 43.80 | 40.90 |
| H5 | 120.00 | 40.90 |
| H6 | 196.20 | 40.90 |
| H7 | 24.75 | 21.85 |
| H8 | 215.25 | 21.85 |

H4–H8 sit at key-grid corners, between switches. Every switch's own NPTH holes are also in the DXF (Ø4.0 centre, Ø1.75 pegs, Ø3.0 socket holes).

## Key grid (layer KEY_CENTERS: centre crosses plus 14.0 × 14.0 plate cutouts)
- 4 rows × 12 columns, 19.05 mm pitch, all 1u.
- Key centre (row r = 0 top … 3 bottom, column c = 0 left … 11 right): **x = 15.225 + 19.05·c, y = 69.475 − 19.05·r**.
- Grid bounding box: x 5.70 → 234.30, y 3.25 → 79.45.

## USB-C (layer USB_C)
- Receptacle on the top side, mouth flush with the **top edge (y = 102)**, centred at **x = 16.00**. The mouth is 8.94 mm wide (x 11.53 → 20.47) and ~3.2 mm tall above the PCB top surface.
- Case opening: suggest 10.5 × 4.5 mm (cable overmould clearance ≥ 12.5 × 6.5 mm outside the wall).

## Encoder (layer ENCODER)
- ALPS EC11E15244G1, vertical, H20: shaft centre **(226.00, 90.00)**, Ø6 mm shaft, M7 bushing.
- The shaft top sits 20 mm above the PCB top surface. Body is 12.0 × 13.5 mm around the shaft. The push switch is in the matrix (pin map ROW4/GPIO18 at matrix position (4,11)).
- Case/plate hole for the bushing: Ø7.5 mm. A knob is not specified yet.

## Other
- **The electronics strip is y 79.5 → 102** (above the key grid, under where the screen hinge goes). It holds the USB-C at x 10.7–21.3, the LDO at x ~31, flash at x ~45, the RP2040 at x 57.8–66.2, and BOOT (86, 94) / RESET (86, 85). It has the encoder at the far right. The tallest parts besides the encoder are the USB-C (~3.2 mm) and the SOT-223 LDO (~1.8 mm).
- BOOT/RESET are only needed for recovery flashing. Either leave a Ø3 mm poke hole over each in the top cover, or let the strip cover come off.
- No parts on the bottom side apart from the hot-swap sockets.
