# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); detailed session records stay
in the ledger. Reviewed through s1195 (2026-08-14).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu explanation is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any new mitigation requires an `ORIGIN:` naming the
  writer and assessing whether the value is legitimate.
- Phase-gated port captures can reach VI width 1024 with independent
  emit/raw/dispatch/match controls. Pre-chain crashes are disjoint families;
  they do not classify parser loss. Ordinary late E9 producer/consumer
  identity is established; synthetic FULL_SYNC was absent in the decisive
  capture. Remaining deltas are boundary/span-shaped and unclassified.
- The recurring `slotDispatcherIter+872` SIGBUS is the generated prologue
  spill of guest `$sp` at `funcs_8.c:22810`. The complete generated audits
  found balanced direct callers, no static indirect target, no runtime `$sp`
  replacement, and no reachable frame-overlapping writer in the audited
  stack, dynamic-copy, wide/narrow/word/partial-store, and load idioms.
  Runtime-side guest memory/value corruption remains open; no mitigation is
  justified.
- The corrected `npcPowerGeneratorUpdate` boundary is sourced as main `.text`
  at `0x80077AF0`; regenerated ELF, N64Recomp output, fixups, and Debug target
  pass. Runtime boundary tests stayed pre-1024 and are unevaluable.
- The complete generated `do_sdl`/`do_sdr` census found five emitted calls.
  The `0x8003A3AC` call lies in the `pows`/`D_8003A4C4` data interval, and the
  four `audioCompandS16` calls lie in a malformed oversized generated body
  with 214 trapped cross-function gotos. No reachable target-path writer or
  frame-overlapping span was established. The helper's aligned-dword merge and
  two-word write are exact by static inspection (single-source evidence).
- M5 audio de-stubbing is closed. Audio remains stubbed. Retail execution
  watches passed whole-RDRAM controls but stayed at VI 320 and never executed
  the four identified `musyxInitVoiceFromSample` writers. Do not reopen without
  a new independent lead reaching audio initialization or voice allocation.
- Retail oracle controls are healthy: whole-RDRAM, scheduled PIF input, and VI
  callback/poll controls pass. The current oracle recipe stalls at width 320 /
  origin `0x006dd280`; its target watches are therefore unevaluable.
- The port VI 640-to-1024 lifecycle is understood as generated state plus host
  VI submission. `applyPendingViChanges` can change selector bytes
  `0x8011A862/0x8011A864/0x8011A865`; a direct `osViSetMode` edge at
  `0x8001B8DC` can submit `0x80128DF0` without entering the selector consumer.
  Host logging independently agrees with the generated pointer and committed
  VI state. The active boot descriptor chain selects the index-0 320 record.
- M4 shade-lane/order is not the cause. Port-side VMADH modeling and an
  independent control matched all 128 lanes. The s1194 producer-chain audit
  accounted for the final operands: `v0` is loaded from the state block and
  `v4` is produced by the documented accumulator chain. H1 (missing operand
  initialization/preservation) is not supported statically; H2 is already
  refuted. H3, a legitimate clipping/saturation sentinel, is the leading
  static explanation, but the exact numeric origin and retail target
  reachability remain open.
- The s1195 paired M4 capture was controlled but phase-unreached. The port
  reached only transient 320/640 widths with zero M4 rows; retail passed its
  whole-RDRAM control but stayed at width 320 and produced zero writes to the
  candidate `0x688:0x710` range. Neither arm selects an M4 hypothesis.

## Active investigation and ranked next steps

1. Resolve M4 phase reachability with one independent oracle execution-mode
   check: pair the debugger-on no-target run with a debugger-off `--vi-poll`
   run (and `--pif-trace` input control) using the verified eleven-Start
   schedule. Do not treat the existing target-watch null as evidence until a
   matching shaded phase is positively reached.
2. Keep audio closed unless a new independent ground-truth lead reaches a
   later audio phase and first passes whole-RDRAM controls.
3. Revisit runtime instrumentation only after a concrete candidate exists.
   Before any probe, read `tools/oracle/README.md` and
   `docs/F5-UCODE-REFERENCE.md`, define positive controls, and phase-gate all
   animated comparisons.

## Durable boundaries

### M3 dispatcher/frame origin

The s1162 census found 144 direct `slotDispatcherIter` calls in 72 generated
callers: all caller entries match companion symbols, stack decrement/increment
pairs balance, and saved `$ra` contracts are present. No static indirect target
to `0x8003E8DC` exists. The former `0x80078894` anomaly is inside the corrected
standalone `npcPowerGeneratorUpdate` boundary. Runtime context ownership has
one executable `r29` initializer in `run_thread_function`; generated and
runtime context audits found no alternate context handoff.

Completed writer/load classes, all with H3 selected and no mitigation, are:

- stack-relative stores, `r29` assignments, dynamic copy/DMA/controller/flash;
- `SD`, `do_swl`/`do_swr`, narrow stores, `MEM_W`, and `MEM_WU`;
- `MEM_D`/`LD`, `do_ldl`/`do_ldr`, and `do_lwl`/`do_lwr`;
- `do_sdl`/`do_sdr` (five emitted sites; all malformed or data-like).

The latest `do_lwl`/`do_lwr` census classified all 418 calls: ordinary pairs
feed bounded structure or stack-local partial stores; unpaired and large or
negative-offset sites are malformed/data-like tails. Their `MEM_W` contract is
exact and no span overlaps the saved frame. The next class is `do_sdl`/`do_sdr`.

### VI descriptor boundary

`osTvType=1` feeds `rsViModeType=0`; the NTSC index window contains mixed
descriptors, while boot selector bytes are `A/B/C=1/0/0`. `initVideoSubsystem`
preserves index 0, copies records to offsets `0x00/0x50/0xA0/0xF0`, and the
generated selector chooses `base+0xF0` (`0x80128E40`), the 320 descriptor.
`osViSetMode_recomp` forwards `ctx->r4` unchanged; the host performs no width
rewrite. This boundary is independently established.

### M4 accumulator boundary

Factor 5 reference data and paired combiner evidence refute an RT64 shade
ordering explanation. The VTXCOLOR payload is nonzero, while decoded shade is
the fixed `0xFFFF8000`/`0x00008000` sentinel. The unresolved issue is the
missing-lighting/vector numeric origin before `vmadh v6,v4,v0`, not RT64 lane
order.

## Superseded conclusions

- The old `H-gate-stale-or-unseen-writer` result was superseded by corrected
  physical-byte samples observing nonzero `0x8011A8A0` at SP send boundaries.
  It was believable because the static census found no generated writer, but
  it did not measure runtime stores.
- The claim that `setViModeType` maps `osResetType` was superseded by generated
  loads and symbols showing `osTvType` at `0x80000300`.
- Fixed-selector, bad-mode-table, and host-logger explanations for width 320
  are closed by the generated descriptor chain and independent retail controls.
- The old boot/menu overlay-dispatch explanation is closed by the current
  mission/post-sec2 behavior and is no longer the active blocker.

## Evidence ledger summary

| Sessions | Durable result |
|---|---|
| s820–s880 | Post-sec2 accounting, breadcrumb, coalescer, and oracle routes classified or parked. |
| s881–s951 | M3 idiom inventories closed the audio-channel-field thread. |
| s952–s983 | Dispatcher stack-spill family localized; oracle callback work repaired later. |
| s984–s1038 | M4 shade source/emission audits and controls moved the issue to accumulator numeric origin. |
| s1039–s1111 | Retail input/cadence and port submit/gate work passed controls; width-320 and pre-1024 paths remained state-shaped. |
| s1112–s1133 | VI lifecycle, descriptor chain, consumer ordering, and regeneration boundary were resolved. |
| s1134–s1140 | M4 paired capture was valid but pre-1024; M3 indirect-call census isolated the old coalesced boundary. |
| s1141–s1161 | VI writer/consumer probes established the direct `applyPendingViChanges` edge and independent host request path. |
| s1162–s1167 | Complete dispatcher-origin runtime attempts were pre-1024 or alternate-failure; no frame writer or RT64 allocation origin selected. |
| s1168–s1171 | MusyX callback/callsite audits found balanced generated contracts and moved the open question to voice sample fields. |
| s1172–s1177 | Retail oracle calibration and execution watches passed controls but stayed at VI 320; audio destination origin remains unevaluable. |
| s1178–s1189 | Complete `$sp`, dynamic writer, store, and load idiom audits selected H3; no frame-overlapping writer or helper broadening found. |
| s1190–s1191 | Partial-load consumer/site rechecks classified all `do_lwl`/`do_lwr` calls and kept H3 selected. |
| s1192 | Maintenance compaction only; no experiment or code change. |
| s1193 | Complete `do_sdl`/`do_sdr` static census selected H3; no reachable frame writer or mitigation. |
| s1194 | Complete M4 final-operand producer-chain audit found initialized `v0` and a contiguous `v4` accumulator chain; H1 unsupported, H2 already refuted, H3 leading but numeric origin remains open. |
| s1195 | Paired M4 port/oracle capture passed independent controls but both arms were phase-unreached; target null unevaluable. |

## Method and safety rules

- A null result is worthless without a positive control in the same run.
- Batch instrumentation; scope counters and budgets to the VI phase; use
  SIGKILL, launch from `build/`, and queue repeat soaks instead of babysitting.
- Regeneration order is `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated code belong in fixup scripts.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. Changes under `lib/` require `./submodule-patches/export.sh`.
- Before mitigation, identify the writer and legitimacy with an `ORIGIN:` line.
