#!/usr/bin/env python3
"""Build the clip-overlay composite ROM (s47).

The Factor 5 gfx ucode swaps code overlays into the IMEM window at 0x1DB0 at
runtime; the recompiled runtime skips IMEM DMAs, so the static translation of
the window region must hold the overlay we want executable. The shipped ROM
keeps the packed overlay-image STORAGE there (init's image at window+8), not
a resident overlay. This script writes a composite ROM whose window region
(ROM 0x26340..0x2655F, IMEM 0x1DB0..0x1FCF) holds the REAL clip overlay
(overlay id 4), whose image lives raw in the ROM at 0x26420..0x2663F —
byte-identical to the runtime RDRAM capture (s47 imem_dma_dump control).

The composite is the input of factor5_rsp_ovl4.toml; RSPRecomp's output
(build/factor5_ucode/factor5_ucode_ovl4_recompiled.c) is consumed by fixup 6
in tools/fixup_factor5_ucode.py, which splices the window translation into
the main ucode as CLIP_* labels.

Usage: python3 tools/make_clip_composite.py   (from the repo root)
"""
from pathlib import Path

root = Path(__file__).resolve().parent.parent
rom = (root / "rogue_squadron.z64").read_bytes()

WINDOW_ROM = 0x26340      # IMEM 0x1DB0 in the main-text image
WINDOW_END = 0x26590      # IMEM 0x2000 (text end)
CLIP_ROM = 0x26420        # overlay id 4 image, OSTask.ucode + 0xE10
CLIP_LEN = 0x220

clip = rom[CLIP_ROM:CLIP_ROM + CLIP_LEN]
out = bytearray(rom)
out[WINDOW_ROM:WINDOW_ROM + CLIP_LEN] = clip
pad = WINDOW_END - (WINDOW_ROM + CLIP_LEN)
out[WINDOW_ROM + CLIP_LEN:WINDOW_END] = b"\x00" * pad   # NOP the old tail

dst = root / "scratch" / "s47_clip_composite.z64"
dst.parent.mkdir(exist_ok=True)
dst.write_bytes(out)
print(f"{dst}: window {WINDOW_ROM:#x}..{WINDOW_ROM+CLIP_LEN:#x} <- clip image "
      f"{CLIP_ROM:#x} ({CLIP_LEN:#x} bytes), {pad:#x} pad bytes zeroed")
