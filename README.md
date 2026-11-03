# Seven Swords Wedge Keyboard

This is an open-hardware 48-key (4 × 12 ortholinear) USB keyboard with an EC11 rotary encoder, built on an RP2040. It's designed for the Seven Swords Wedge desk console by Seven Swords Productions.

| Path | What | Licence |
|---|---|---|
| `keyboard-pcb/` | KiCad 9 project: schematic, PCB, generator scripts, fab outputs, outline DXF | **CERN-OHL-P-2.0** (`keyboard-pcb/LICENSE`) |
| `firmware/` | RMK-based Rust firmware (`rmk-wedge/`) and prebuilt UF2 | **MIT** (`firmware/rmk-wedge/LICENSE`) |

See `keyboard-pcb/README.md` for the build and fab instructions, and `keyboard-pcb/NOTICE.md` for attributions. The RP2040 core follows the Raspberry Pi "Minimal RP2040" reference design (MIT). Raspberry Pi is a trademark of Raspberry Pi Ltd. This is not a Raspberry Pi product.

USB IDs: the firmware currently uses RMK's test VID/PID. A pid.codes ID (1209:5357) is planned and not yet assigned.
