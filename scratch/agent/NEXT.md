# NEXT: FIX DIAGNOSTIC CAPTURE BOUNDS AND VERIFY THE WINDOW
HYPOTHESIS-ID: g3-hangar-artifacts

s6607 completed the requested writeback census in retail and wide16 (12 MB).
The narrow no-writeback hypothesis is refuted: hangar wide sources have 48
and 25 intersecting writebacks, each changing the watched columns. Neither
arm's initial source fingerprints match a preceding writeback post hash.
Do not repeat this census or call overlap an artifact attribution.

The decisive correction: raw dumps exceed the actual logged source height.
Retail: 512x358 vs 512x336. Wide16: 796x448 vs 796x336. Same-frame wide
bottom garbage lies below the 336-row boundary; the dump code explicitly
forces 448 rows. The previous column ROI is not that bottom band.
See docs/owner_sheet_s6607_capture_bounds.png. This is a capture diagnosis,
not proof of what the RT64 window displays, and not a rendering fix.

ONE bounded change: correct the existing framebuffer dumper to derive its
height/layout from the actual VI/source geometry instead of width heuristics.
Keep the raw dump's provenance and log base, stride and dimensions. Read the
RT64 shape calculation first; reuse its semantics rather than a hangar-only
336 constant. Preserve paired-row retail modes and validate the title too.

Competing hypotheses and discriminator, written before building:
- H-dump-overread: garbage exists only in rows outside the actual source;
  correctly bounded dump and an actual window capture both lack it.
- H-window-present: bounded source is clean but actual window still shows
  a band; presentation/layout is the remaining owner.
- H-real-source: the same visible band exists within both bounded source
  and window; only then pursue the producing RDP/guest writer.
The positive control is actual image content plus a deliberately oversized
reference crop showing the known tail. Match by VI transition/source address,
not dump ordinal or elapsed time. A nonzero hash alone is not a control.

Preparation/build:
```sh
rg -n 'const uint32_t dh|source=rdram-readback|s_fbd_vi' src/main/upstream_compat.cpp
rg -n 'screenFbSize|screenFbAddress|VI.*[Ss]ize' lib/rt64/src/hle/rt64_state.cpp
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
```
Reference recipe (capture driver lives in scratch and has no build changes):
```sh
python3 scratch/agent/s6607_band_wb_run.py
python3 tools/g3_hangar_writeback.py scratch/agent/s6607_band_wb/retail/run.log scratch/agent/s6607_band_wb/wide16/run.log
```
Use NEW output paths for the next run; preserve s6607 artifacts. Arm retail
and ASPECT=16:9 with OSMEM_MB=12 from the same binary, one game at a time,
phase-gated autopilot as in the driver, screen unlocked. Capture the actual
window using a window screenshot (e.g. screencapture -x -l <window-id> PATH),
not a PPM read of guest RAM. Check screenshot permission before starting;
a denial is not evidence about rendering. SIGKILL game at the deadline.
Do not add a rendering guard, cull or default change.
