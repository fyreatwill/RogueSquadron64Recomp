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

Usage: python3 tools/make_clip_composite.py [4|12]   (from the repo root)
"""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
rom = (root / "rogue_squadron.z64").read_bytes()

WINDOW_ROM = 0x26340      # IMEM 0x1DB0 in the main-text image
WINDOW_END = 0x26590      # IMEM 0x2000 (text end)
OVERLAYS = {
    4: (0x26420, 0x220, "clip"),
    12: (0x26670, 0x230, "trigen"),
}

overlay_id = int(sys.argv[1], 0) if len(sys.argv) == 2 else 4
try:
    overlay_rom, overlay_len, overlay_name = OVERLAYS[overlay_id]
except KeyError:
    raise SystemExit(f"unsupported overlay {overlay_id}; choose one of {sorted(OVERLAYS)}")

overlay = rom[overlay_rom:overlay_rom + overlay_len]
out = bytearray(rom)
out[WINDOW_ROM:WINDOW_ROM + overlay_len] = overlay
pad = WINDOW_END - (WINDOW_ROM + overlay_len)
out[WINDOW_ROM + overlay_len:WINDOW_END] = b"\x00" * pad

dst = root / "scratch" / f"s47_{overlay_name}_composite.z64"
dst.parent.mkdir(exist_ok=True)
dst.write_bytes(out)
print(f"{dst}: window {WINDOW_ROM:#x}..{WINDOW_ROM+overlay_len:#x} <- "
      f"overlay {overlay_id} image {overlay_rom:#x} ({overlay_len:#x} bytes), "
      f"{pad:#x} pad bytes zeroed")
