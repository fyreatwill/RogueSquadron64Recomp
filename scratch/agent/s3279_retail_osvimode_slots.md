# Session 3279 — retail OSViMode table holds 1024 at title

HYPOTHESIS-ID: m5-osvimode-retail-1024-slot

## Competing hypotheses

- `H-RetailTableHas1024`: while title `1024 @ 0x00790400` is live, at least
  one of the four slot +8 words is 1024. The port is missing that rewrite.
- `H-RetailTableNever1024`: title 1024 is reached and the whole-RDRAM
  control fires, but no 1024 store lands in those four +8 words. Title 1024
  is not published from this table.
- `H-RetailTableCoverageInvalid`: whole-RDRAM control or title 1024 gate
  missing; no slot conclusion.

## What ran

Independent retail oracle, Rice video, eleven-Start schedule. Watches are
physical. Slot +8 words: `0x00128D58/DA8/DF8/E48`. Same-run controls:
`--watch-write 0x0:0x800000` (cap 10000, then removed) and `--vi-trace`.
`--detail-watch 1..4` so slot stores still print after the cap.
`--post-value-watch 1..4` plus a title-window snapshot so the 1024-edge
store is not lost to hangar overwrite.

Dummy-video arm (no `--video`) stayed at `320 @ 0x006dd280` for 60 s with
3595 VI. That is the documented dummy-RDP stall, not a slot conclusion.
Rice is required for any phase past boot 320.

No audio behavior change. No M5 Step 3. No `PatchesLib` build.

Captures:
- `scratch/agent/s3279_retail_osvimode_slots.log` (60 s Rice)
- `scratch/agent/s3279_retail_osvimode_slots_title.log` (25 s Rice, title window)
- `scratch/agent/s3279_retail_osvimode_slots_dummy.log` (dummy-video control)

## Same-run positive controls

60 s Rice: whole-RDRAM watch reached 10000 and was removed; slot watches
stayed armed. VI: `320 → 640 @ 0x0066A500` (2.4 s) → `1024 @ 0x00790800`
(17.3 s, then `0x00790400`) → hangar `512 @ 0x006AB400` (38.4 s). 3563 VI.

25 s Rice: same 10000-write control; stopped during title 1024 (last origin
`0x00790400`); 1461 VI; never reached hangar. Phase bucket
`1024 @ 0x00790400` had 234 VI.

Snapshot FNV decoder was checked in-session against known words:
`0x140`→`0x4a95f3c2` (dummy 320 match), `0x200`→`0x4995f1ef` (hangar
sampled `0x00000200` match), `0x400`→`0x4795eec9`.

## Slot stores

Every slot +8 word is written only by `0x8001B6B0` (`initVideoSubsystem`
4×0x50 copy, same PC as the port's 320→640 rewrite at `0x8001B6A8`).
Six copies in 60 s, four in the 25 s title window:

| t (60 s) | VI width change | sampled post-value |
|---:|---|---|
| 0.8 s | boot 320 | unsampled (pre-arm) |
| 2.4 s | 320→640 | unsampled |
| 7.0 s | still 640 | unsampled |
| 17.3 s | 640→1024 | unsampled (store precedes first 1024 VI callback) |
| 38.4 s | 1024→512 | `0x00000200` (512) |
| 52.9 s | hangar 512 | `0x00000200` (512) |

Post-value arms only at title 1024 or hangar 512, so the 17.3 s title
rewrite is visible only in the title-window snapshot.

## Title-window snapshot (25 s, 1024 live)

All four slots: `bytes=4 nonzero=1 fnv=0x4795eec9` = word `0x00000400`
(1024). No hangar rewrite had occurred (4 writes/slot, last at 17.2 s).

Hangar-complete snapshot (60 s): all four slots `fnv=0x4995f1ef` =
`0x00000200` (512), matching the two armed post-value samples.

## Classification

- `H-RetailTableCoverageInvalid` is refuted by the Rice arms (whole-RDRAM
  10000 + title `1024 @ 0x00790400`). The dummy arm is the predicted
  dummy-video stall, not a slot result.
- `H-RetailTableNever1024` is refuted: while title 1024 is live, every
  slot +8 word is 1024.
- `H-RetailTableHas1024` is selected. Combined with Session 3278's port
  census (slots 320 then 640, never 1024), `H-MissingTableRewrite` is now
  two-source for the table-contents difference.

This does not yet say the missing 1024 copy is why the port stays at
VI 640. Retail's 1024 copy is at the 640→1024 edge, so it may be part of
title entry (symptom) rather than a pre-title publisher the port should
already have run (cause). Next discriminator: caller of
`initVideoSubsystem` (`0x8001A098`) at that 1024-edge copy.
