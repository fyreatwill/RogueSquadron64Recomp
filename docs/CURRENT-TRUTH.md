# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Historical
detail from s4269 onward is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) and
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md).

Updated for session 4358 (2026-10-09). The preceding maintenance pass reduced
this file to durable state; session 4357 qualified phase coverage but exposed a
retail task-join instrument boundary.

## Current state

The qualified native route boots through attribution, N64 logo, intro cinematic,
Factor 5 logo, title VI 1024 (`0x00790400`) and hangar VI 512 (`0x006AB400`)
on the real-audio/LLE/ungated/solo/spin-yield route. `ROGUESQ_AUDIO_UCODE=0`
is the silent control. VI 640 is the intro, not a stuck state. Hangar
geometry/colour artifacts remain.

Audio is no longer a zero-output stub on the qualified route. Fresh 7F saves
produce nonzero PCM; reset `build/saves` before audio A/B and use
`RS64_EEP_TRACE=1`. AI byte order is fixed (`p[i ^ 3]`, `queue_samples ^ 3`);
876/894 title AI buffers matched ucode output in the qualified capture.
MusyX/MORT remains only partially de-stubbed and must not reach stock
`aspMain`.

M5 Step 9 is at a qualified retail selector/decode boundary. The port's
descriptor/filter route is reachable at generated callsite `0x8009D740`; the
seeded silent/real matrix reaches hangar and has independent MORT, whole-RDRAM,
and VI controls. Its later descriptor pointers, words, type/class sequence,
source/output hashes, and branch fields diverge between arms. This rejects a
post-filter-only explanation and leaves the pre-filter stream/selector
boundary open.

Session 4358's repaired C904/C950 join capture passed the retail whole-RDRAM
control and reached the hangar phase. C904/C950 witnesses were live (512
bounded rows), but the existing `0x80033FCC` task watch produced zero task
rows, so the new phase-keyed C904/C950-to-task join produced zero matches and
zero rows. This is a stronger instrument-boundary result: the retail source
boundary is live while the presumed task consumer PC is absent in the same
qualified route. The port arm independently remained live through hangar with
task/ABI and image-DMA joins. It does not select pre-filter origin or
selector-consumer divergence yet; the next probe must locate the actual retail
task consumer PC around the presumed `0x80033FCC` handoff.

Session 4357's established consumer matrix passed the retail whole-RDRAM
control (33,331,419 writes), reached title and hangar, and completed 4,478 VI;
the port reached title 1024 at 13.7 s and hangar 512 at 34.0 s without a
crash/abort. The retail task/field join at `0x80033FCC` produced zero rows,
while the port produced 2,817 ABI rows and 2,812 DMA joins. This is an
instrument-boundary result, not evidence for either stream-origin hypothesis;
the next probe must repair the retail join at the already-qualified C904/C950
witnesses.

The independent retail witness at `0x8009C904`/`0x8009C950` reached title and
hangar, with 10,000 whole-RDRAM control writes and 3,107 C904 executions.
Session 4352 retained `branch_state=0x3108` in 584 rows and `0x0010` in 405
rows. Selected words and decoded `+0x18A/+0x18C` fields varied. The configured
post-value watch was mistakenly limited to caller return PCs
`0x8009C0E8..0x8009C0EC` and fired zero times; that is an instrument-boundary
result, not evidence against a writer. The s4354 bounded physical writer watch
passed the whole-RDRAM positive control and retained C904/C950 coverage, but
recorded only 150 stores at `0x1535AC..0x1535BC` and zero stores in the
selected-address subrange `0x1535C4..0x1545C0`. The s4355 run independently
watched both reads and writes: it qualified 10,820 whole-RDRAM writes, 3,107
C904 executions, 7,182 VI frames, and 40,179 reads in the broad range, while
sampled writer PCs emitted only the lower metadata-prefix stores. The bounded
source audit likewise found no direct store to `0x1535C4..0x1545C0` in the
C904 caller/callee path. This closes the post-C904 selected-range writer
hypothesis for the qualified route; the broad watch must not be interpreted as
820 distinct upper-range writes.

Earlier qualified retail work rejected the source span, base/index, route alias,
and stable base-buffer as the retained family producer. `+0x198` settled on
base `0x801B2C60`; `+0x11C8` advanced under `0x8009D790`; selected base-buffer
contents reached `0x801B4CE0` without carrying the family. The lattice store at
`0x8009DB2C` is legitimate quantized output, not the semantic family writer.
The next boundary is therefore the bounded selector/decode writer range.

The RT64 framebuffer-set growth root is a bump-time DPC ring-lap placeholder
drop; `ROGUESQ_WRAP_RESTORE` reproduced ODD-cimg reduction from 60 to 0 in
three runs, but hangar impact remains unqualified. Do not broaden this line
ahead of the M5 selector work. The VI-640 crash family and M3 guard classes are
parked; no mitigation is authorized without an ORIGIN writer and legitimacy
assessment.

The full regeneration flow is unsafe since s4204: `N64Recomp ->
fixup_game_funcs.py` aborts at the E088 anchor and can clobber live generated
functions. Use the existing `tools/apply_s*.py` workflow unless the regen issue
is explicitly repaired.

## Next steps

1. **M5 selector/decode boundary** — HYPOTHESIS-ID
   `m5-selector-decode-boundary`. Locate the actual phase-qualified retail
   task-consumer PC with one bounded execution-range census around the absent
   `0x80033FCC` handoff, retaining C904/C950, whole-RDRAM, VI, and port task/DMA
   controls. A live nearby task PC with C904 joins selects the consumer-boundary
   route; no nearby task PC despite C904 and controls selects a wider
   instrument-boundary explanation; a task row whose source fields already
   differ selects H-pre-filter-origin.
2. M3 pre-publication guard runtime qualification, blocked until a host with
   `mips64-elf-gcc`, `mips64-elf-ld`, and `PatchesLib` is available.
3. Generated-symbol renaming sweep, slug `generated-symbol-renaming-sweep`,
   only when items 1–2 are inapplicable; mapping-only edits do not reset the
   engineering-change gate.

## Live hypotheses

| Hypothesis | Status |
|---|---|
| M5 selector/decode family origin | H-earlier-stream confirmed for the qualified route by source audit plus retail read/write attribution: no direct post-C904 store reaches `0x1535C4..0x1545C0`; sampled stores stop at `0x1535AC..0x1535BC`. |
| M5 consumer join | Retail C904/C950 witnesses are live, but both the prior task/field join and the s4358 repaired C904/C950-to-task join have zero task rows at `0x80033FCC`; the presumed consumer PC is absent and the actual consumer boundary remains open. |
| M5 audio-task-rate divergence | Single-source qualified port A/B shows no useful split: title/hangar phase transitions were both 15.0/24.2 s, and the first hangar sequence was 1064 image versus 1056 silent. Lifetime-row caps prevent an exact 18–28 s count, so this is qualified rate-equivalence evidence, not final cross-source closure. |
| M5 producer provenance | Port hangar source span is cleared by legitimate ROM-DMA/`rs_memset`; no mitigation. |
| Retail/port post-free stream layout | Retail and port share the first qualified read/free boundary, then diverge in later layout/value/order; exact consumer cause open. |
| RT64 fb-set growth | Source is the DPC bump-time placeholder-drop class; hangar effect open. |
| VI-640 crash writer | Open, independent of audio ucode/private DMEM; writer unnamed. |
| M3 sentinel ownership | Source-scope H1 only; runtime unqualified without MIPS toolchain. |

## Evidence boundary and operating rules

Retail oracle watches are physical-address ground truth. Whole-RDRAM, VI, and
target-PC controls qualify coverage; a route failure invalidates a null. Every
instrument needs an independent witness, same-run positive control, phase-scoped
budget, and (before promotion to truth) a second evidence line. Phase-gate
animated comparisons on VI transitions and batch A/B arms in one build/run.

Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX
assumptions. The graphics path is LLE-only. Keep safety guards separate from
explanations. Regeneration order is `make_elf.py -> N64Recomp ->
fixup_game_funcs.py -> CMake`; never hand-edit generated functions for behavior.
If `lib/` changes, export submodule patches. Never run submodule update,
checkout, clean, or hard reset. Kill runs with SIGKILL and run from `build/`.
Any mitigation-shaped change needs an `ORIGIN:` line naming its writer and
whether the value is legitimate.

## Evidence index

[M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md),
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md),
[PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md), and the append-only detailed ledger
in [PORTING-STATE.md](../PORTING-STATE.md). Use bounded grep/sed windows for
the ledger; do not read it whole.
