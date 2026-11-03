# Seven Swords Wedge keyboard firmware (RMK)

Firmware for the Wedge's own 48-key RP2040 board (`../keyboard-pcb`). It is built on
[RMK](https://github.com/HaoboGu/rmk) 0.9.0 (MIT OR Apache-2.0, pulled from crates.io; none of it is vendored here).
Everything about the keyboard lives in `rmk-wedge/keyboard.toml`. `src/main.rs` is just RMK's macro.

Status: **it compiles** (2026-11-03, rustc stable, `thumbv6m-none-eabi`, 134,828 bytes of flash text). It has **not run on hardware**
yet, because no board exists.

## Pin map (must match keyboard-pcb/gen/design.py)

| Signal | GPIO | Notes |
|---|---|---|
| COL0..COL11 | GPIO0..GPIO11 | columns, driven (COL2ROW) |
| ROW0..ROW3 | GPIO12..GPIO15 | rows, read; 1N4148W cathode on the row |
| ROW4 | GPIO18 | encoder push only: matrix key (4,11), on COL11 through D49 |
| ENC_A / ENC_B | GPIO16 / GPIO17 | EC11 quadrature, common pin to GND, internal pull-ups |
| SWCLK / SWDIO | SWD pads | J2 is **DNP, do not fit** (a header collides with the case plate). Pogo onto the pads only with the board out of the case |

The encoder push sits **in the matrix** rather than on its own direct pin. RMK can't mix a normal
matrix with direct-pin keys in `keyboard.toml`, so putting the push in the matrix keeps the firmware to pure config.

## Keymap (3 layers)

* **base**: ortho QWERTY. The bottom row is `Ctrl Gui Alt `` LOWER Space Space RAISE ← ↓ ↑ →`.
* **lower**: numbers, `- = [ ] \`, Delete, Home/End/PgUp/PgDn.
* **raise**: F1–F12, CapsLock, PrintScreen.
* **Encoder**: on base, turn = PageDown/PageUp and push = **F6** (cycles panes in `ssp-wedge-term`). On lower it does volume, and on raise it does ←/→.
* Vial live remapping is on. Unlock = hold Esc + Backspace. Edits are stored in flash.

## Build

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh   # once
rustup target add thumbv6m-none-eabi
cargo install flip-link                # stack-overflow-safe linker used by .cargo/config.toml
cd rmk-wedge
cargo build --release
```

The output is `rmk-wedge/target/thumbv6m-none-eabi/release/ssp-wedge-kb` (ELF).

## Make a UF2 and flash it over USB (no probe needed)

```bash
OBJCOPY=$(ls ~/.rustup/toolchains/stable*/lib/rustlib/*/bin/llvm-objcopy)   # rustup component add llvm-tools
$OBJCOPY -O binary target/thumbv6m-none-eabi/release/ssp-wedge-kb ssp-wedge-kb.bin
python3 tools/bin2uf2.py ssp-wedge-kb.bin ssp-wedge-kb.uf2
```

1. Hold **BOOT** (SW49), tap **RESET** (SW50), then let go of BOOT. An `RPI-RP2` drive appears. In the Wedge case, press both with a SIM-eject pin through the two Ø3 plate holes (BOOT over PCB (86, 94), RESET over (86, 85)). You don't need to open the case.
2. Copy `ssp-wedge-kb.uf2` onto the drive. The board reboots as "Seven Swords Wedge KB".

Prebuilt copies from this build are in `dist/` (`ssp-wedge-kb.uf2`, `.bin`). Both are untested on hardware.

You can also install `elf2uf2-rs` and run `cargo run --release` while the board is in BOOTSEL mode,
or use a debug probe with `probe-rs` (see `.cargo/config.toml`). J2 is DNP, so this means pogo pins on the bare SWD pads with the board out of the case.

## Before selling

* `vendor_id = 0x4c4b`, `product_id = 0x4643` are RMK's shared test IDs. A commercial product needs its own USB VID/PID,
  either from the USB-IF (paid) or as a sub-licensed PID such as pid.codes for open hardware. pid.codes was chosen (2026-11-03).
  The application for **0x1209 / 0x5357** is drafted but not submitted, so the PID is NOT assigned. Keep the test IDs until the
  pid.codes PR is merged. Then set `vendor_id = 0x1209`, `product_id = 0x5357`.
* The encoder `resolution = 2` matches the BOM encoder, ALPS EC11E15244G1 (30 detents, 15 pulses: 15*4/30 = 2). If you fit a different EC11, set resolution = pulses*4/detents.

## Licence

Our files (keyboard.toml, build.rs, main.rs, tools/) are MIT, Copyright (c) 2026 Seven Swords Productions.
`memory.x` is adapted from RMK's rp2040 example (MIT OR Apache-2.0). RMK and its dependencies keep their own licences.
