# Resident overlay 12 provenance audit

Static audit completed 2026-08-12 (s738). The active section-2 reset route
is `L_15AC -> L_1268(r5=0x0C) -> L_1298 -> 0x1DB0`. The dispatcher uses the
high nibble of `DMEM[0x7A + r5]` as an index into the halfword table at
`DMEM[0x76]`; for the overlay-12 route that table entry is the shared IMEM
window address `0x1DB0`.

| Resident image | Raw ROM image | Length | `L_1DB0` behaviour | Runtime route |
|---|---:|---:|---|---|
| 04 control | `0x26420` | `0x220` | clip implementation, saves `ra` and enters its clip work loop | explicit `CLIP_*` splice |
| 0C treatment | `0x26670` | `0x230` | consumes TriGen-adjacent parameters, DMA-loads two payloads, then continues its vector loop | falls through to main `L_1DB0` |
| main/static | ROM text window `0x26340` | shared | clears `DMEM[0x152]`, resets state, and enters the DPC continuation | used incorrectly for resident 0C |

The historical IMEM-DMA capture gives the independent source mapping:
overlay 12 is the stable `dram=0x25A70`, `len=0x230` window image and all
window images map byte-for-byte to `ROM = dram + 0xC00`. This audit rebuilt
both composite arms with `tools/make_clip_composite.py`: the resident-04
positive control and resident-0C treatment exactly matched their ROM ranges,
then RSPRecomp translated each with the same window address. The generated
overlay-12 `L_1DB0` starts with `lbu -0x6($17)`, conditional `L_1F64`, and
two `L_122C` DMAs sourced from the command stream. It contains no
`DMEM[0x152]=0` reset. The generated main-image `L_1DB0` performs that reset
before its DPC path.

Verdict: **H-stale-main-image selected.** **H-intended-resident0c-reset** and
**H-bad-table-entry** are refuted: the table correctly chooses the shared
window entry and the correct resident-0C image at that entry is different.
The runtime deliberately skips IMEM-targeted DMA and only restores resident
04 through the existing clip splice, so resident 0C executes the wrong static
image. This is the writer of the observed depth reset: main `L_1DB0`, not the
overlay-0C TriGen code.

s739 landed that splice (fixup 6b, `OVL12_*`, resident `0xC` at `0x1DB0`,
jal-return cases `0x1DD8/1DF4/1F9C/1FAC/1FBC/1FCC`). Build-time extraction
and helper-set checks passed. Live section-2 validation is
`scratch/agent/soak_queue/s739_ovl12_splice.sh`.
