# NOTICE: Seven Swords Wedge keyboard PCB

The Seven Swords Wedge keyboard PCB is original work by Seven Swords Productions. It was generated from `gen/*.py`.

## Licence
- **This hardware design** (KiCad project, `gen/` scripts, `lib/` footprint, `route/`, `mech/`, `fab/`, `reports/`, `renders/`): **CERN-OHL-P-2.0**, Copyright (c) 2026 Seven Swords Productions. The full text is in `LICENSE`. SPDX-License-Identifier: CERN-OHL-P-2.0. The same identifier is on the PCB silkscreen ("CERN-OHL-P-2.0 (c) 2026 Seven Swords Productions") and on the schematic and PCB title blocks.
- **Keyboard firmware** (`../firmware/rmk-wedge`): MIT, Copyright (c) 2026 Seven Swords Productions. `memory.x` is adapted from RMK's rp2040 example (MIT OR Apache-2.0). RMK itself is MIT OR Apache-2.0 and is pulled from crates.io, not vendored.
- **Bot app** (`ssp-wedge-term`): MIT, separate.

Under CERN-OHL-P you may use, copy, modify, make and distribute this design and products made from it. Keep this notice and the licence text with any copy of the sources, and keep the licence/copyright marking on the board. There is no warranty (CERN-OHL-P §6).

Trademarks: Raspberry Pi is a trademark of Raspberry Pi Ltd. The product is "Seven Swords Wedge". The board's silkscreen mention of the "Raspberry Pi Minimal RP2040" design is an attribution only, not a product name and not an endorsement.

## Third-party design reference: RP2040 core circuit
The RP2040 support circuit follows Raspberry Pi's "Minimal RP2040" reference design, `RPI-RP2040-MINIMAL_R3-S1`. That covers the 1.1 V/3.3 V decoupling, the 12 MHz crystal, the QSPI flash, the BOOT/RESET buttons and the USB series resistors. Our values and layout are our own: for example, 33 pF crystal load caps to suit our crystal, an AMS1117 LDO, and our own placement. We copied no files from that design. The circuit is credited here as its licence asks:

```
= Disclaimer =
This design is provided under the MIT license included at the end of this file. The design may incorporate individual elements that have been provided by third parties with permission to redistribute. No additional license terms are imposed by this use of third party provided elements, where applicable.

The overall design and any individual elements incorporated into the whole, whether created by first or a third party, are provided here for guidance only and without guarantee. Any third party intending to use the provided design for appearance and fitment purposes must refer to manufacturer information and conduct suitable measurements of the physical product.

= MIT License =
Copyright (c) 2026 Raspberry Pi Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

## KiCad libraries
Footprints and symbols come from the stock KiCad 9 libraries (CC-BY-SA 4.0 with the KiCad library exception, which lets you use them in your own designs with no attribution or share-alike on the design). The hot-swap socket footprint `SSP_Wedge:SW_MX_Hotswap_Kailh_1.00u` is our own. It was drawn from the Kailh CPG151101S11-16 datasheet dimensions.

## Tools
Freerouting 2.5.0 (GPL-3.0) was run as a separate program to autoroute the board. Its output (`route/*.ses`, tracks only) is our design data. No Freerouting code is part of this project.

## Not used
Nothing from Micro Journal (CC BY-NC) or any other keyboard project was copied.
