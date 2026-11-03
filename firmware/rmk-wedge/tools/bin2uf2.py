#!/usr/bin/env python3
"""Pack a flat RP2040 flash image (starting at 0x10000000) into UF2 for the BOOTSEL drive."""
import struct, sys
FAMILY_RP2040 = 0xE48BFF56
src, dst = sys.argv[1], sys.argv[2]
data = open(src, "rb").read()
data += b"\0" * (-len(data) % 256)
n = len(data) // 256
with open(dst, "wb") as f:
    for i in range(n):
        hdr = struct.pack("<IIIIIIII", 0x0A324655, 0x9E5D5157, 0x00002000, 0x10000000 + 256 * i, 256, i, n, FAMILY_RP2040)
        f.write(hdr + data[256 * i:256 * (i + 1)] + b"\0" * 220 + struct.pack("<I", 0x0AB16F30))
print(f"{dst}: {n} blocks, {len(data)} bytes")
