#!/usr/bin/env python3
"""Build a Factor 5 IMEM-overlay composite ROM.

The Factor 5 gfx ucode swaps code overlays into the IMEM window at 0x1DB0 at
runtime; the recompiled runtime skips IMEM DMAs, so the static translation of
the window region must hold the overlay we want executable. The shipped ROM
keeps the packed overlay-image STORAGE there (init's image at window+8), not
a resident overlay. This script writes a composite ROM whose window region
(ROM 0x26340..0x2655F, IMEM 0x1DB0..0x1FCF) holds the REAL clip overlay
(overlay id 4), whose image lives raw in the ROM at 0x26420..0x2663F —
byte-identical to the runtime RDRAM capture (s47 imem_dma_dump control).

The overlay-4 composite is the input of factor5_rsp_ovl4.toml; its RSPRecomp
output is consumed by fixup 6 in tools/fixup_factor5_ucode.py. The overlay-12
composite is the input of factor5_rsp_ovl12.toml and is consumed by fixup 6b.
Overlay 24 is dest 0x12A0 (not the 0x1DB0 window): the composite overwrites
only that IMEM range so RSPRecomp labels the emit image at the hardware dest.
Fixup 6c extracts that range; it does not overwrite main L_12A0.
Overlay 14 is dest 0x1DB0 (ROM 0x26AB8, table len 0x21F -> 0x220 B): a
vector loop that exits j L_1268; ori $5, 0x18. Fixup 6g extracts that
window and routes DMEM 0x153 == 0x14.
Overlay 18 is dest 0x1DB0 (ROM 0x26CD8, table len 0x21F -> 0x220 B):
ovl14's successor, exits j L_1268; ori $5, 0x10. Fixup 6h extracts
that window and routes DMEM 0x153 == 0x18.
Overlay 10 is dest 0x1DB0 (ROM 0x268A0, table len 0x213 -> 0x214 B):
ovl18's successor, first word 0x9626000C, no jals, exits
j L_1268; ori $5, 0x1C at IMEM 0x1FBC plus j L_15D0 at 0x1F38.
Fixup 6i extracts that window and routes DMEM 0x153 == 0x10.

Usage: python3 tools/make_clip_composite.py [4|10|12|14|16|18|24]   (from the repo root; 16==10)
"""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
rom = (root / "rogue_squadron.z64").read_bytes()

WINDOW_ROM = 0x26340      # IMEM 0x1DB0 in the main-text image
WINDOW_END = 0x26590      # IMEM 0x2000 (text end)
# source_rom, copy_len, name, dest_rom, pad_end_or_None
# dest 0x12A0 = text_offset 0x25610 + (0x12A0-0x1080) = 0x25830
OVERLAYS = {
    4: (0x26420, 0x220, "clip", WINDOW_ROM, WINDOW_END),
    10: (0x268A0, 0x214, "ovl10", WINDOW_ROM, WINDOW_END),
    12: (0x26670, 0x230, "trigen", WINDOW_ROM, WINDOW_END),
    14: (0x26AB8, 0x220, "ovl14", WINDOW_ROM, WINDOW_END),
    18: (0x26CD8, 0x220, "ovl18", WINDOW_ROM, WINDOW_END),
    24: (0x27260, 0xE4, "ovl24", 0x25830, None),
}

overlay_id = int(sys.argv[1], 0) if len(sys.argv) == 2 else 4
# 0x10 is 16 decimal; accept both the hex-digit key (10) and the decimal id (16).
if overlay_id == 16:
    overlay_id = 10
try:
    overlay_rom, overlay_len, overlay_name, dest_rom, pad_end = OVERLAYS[overlay_id]
except KeyError:
    raise SystemExit(f"unsupported overlay {overlay_id}; choose one of {sorted(OVERLAYS)} (or 16 for ovl10)")

overlay = rom[overlay_rom:overlay_rom + overlay_len]
out = bytearray(rom)
out[dest_rom:dest_rom + overlay_len] = overlay
pad = 0
if pad_end is not None:
    pad = pad_end - (dest_rom + overlay_len)
    out[dest_rom + overlay_len:pad_end] = b"\x00" * pad

dst = root / "scratch" / f"s47_{overlay_name}_composite.z64"
dst.parent.mkdir(exist_ok=True)
dst.write_bytes(out)
print(f"{dst}: dest {dest_rom:#x}..{dest_rom+overlay_len:#x} <- "
      f"overlay {overlay_id} image {overlay_rom:#x} ({overlay_len:#x} bytes)"
      + (f", {pad:#x} pad bytes zeroed" if pad else ", no pad (leave main tail)"))
