# Session 3308 — cinematicStageAdvancer skips on $v1==0 at 0x800AF55C

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

## Competing hypotheses

- `H-PtrZeroSkip`: `0x800AF55C` sees `$v1==0` (word at `0x800B0934`)
  and takes `L_800AF604`; the stage/dt path never runs.
- `H-DtBelowThreshold`: the `c.lt.s` at `0x800AF588` stays false;
  stage byte `0x800B0938` never increments.
- `H-StageNeverHits7`: stage byte increments but `sltiu 0x7` at
  `0x800AF5B0` stays true; exit `$v0` never published.
- `H-CoverageInvalid`: missing mark-all, viewer-return, VI-640,
  cinematic-entry, loop-head, or gate row.

## What ran

One regeneration-safe table covering entry `0x800AF550`, ptr-check
`0x800AF55C`, fp-compare `0x800AF590`, stage-lt7 `0x800AF5B4`,
ret-one `0x800AF5BC`, and ret-zero `L_800AF604`. Live apply:
`tools/apply_s3308_stage_advancer.py` into `funcs_29.c`. The same
transform is imported by `N64Recomp/fixup_game_funcs.py`. Diagnostic
only: no guest store/branch change, no M5 Step 3. s3306 loop table
kept.

The first launch (`run1_crash.log`) died at 4 s with
`spTaskSchedulerThread` SIGSEGV at VI 320 (`last-guest-pc=0x8000834c`,
`si_addr=0x400128d47`) before marks. That run is coverage-invalid.
The same-binary retry (`run.log`, 120 s watchdog) is the live scope.
Driver: `scratch/agent/s3308_stage_advancer/run.sh`.

Queued soak `s3307_cine_loop_600s` (folded here): 600 s SIGKILL, no
crash, no title 1024, exit-gate `v0_nz=0`, last printed cine-loop
n=100, scheduler still matching recv at width 640 origin `0x696100`.

## Same-run positive controls (120 s retry)

- `[s3308-stage-adv-control] mark` IDs 0–5 (6/6).
- `[s3306-cine-loop-control] mark` IDs 0–6 (7/7).
- `[s3305-postviewer-control] mark` IDs 0–23 (24/24).
- `arm=completion-wins-default` 61; `requested_pre=1 requested_post=0` 61.
- `[event-wiring] complete kind=SP` 64.
- `[phase] vi_width=640 (was 320) origin=0x0066A500` at 2.6 s `#102`.
- Viewer `[m5-postwait]` entry and return.
- s3305 cinematic-entry; s3306 loop-head and exit-gate.
- Zero `[CRASH]` / `[ABORT]` on the retry.

## Port cinematicStageAdvancer (live retry)

| n | site | `$v1` / `$v0` | taken | notes |
|---|---|---|---|---|
| 1–100 printed | entry `0x800AF550` | — | 0 | `$a2` 1/60 then 1/30 |
| 1–138 | ptr-check `0x800AF55C` | **`$v1=0`** | **1** | all 138 skip |
| 0 | fp-compare `0x800AF590` | — | — | silent |
| 0 | stage-lt7 `0x800AF5B4` | — | — | silent |
| 0 | ret-one `0x800AF5BC` | — | — | silent |
| 1–100 printed | ret-zero `0x800AF604` | `$v0=0` | 0 | skip return |

s3306 exit-gate printed n=100 all `$v0=0` `taken=0`. Silent: 64BC,
6618, title 1024.

Guest `lw $v1, 0x934($v0)` with `$v0=0x800B0000` is the live load.
The helper's independent `MEM_W(0x800B0000, 0x934)` printed
`ptr=0x6E6F6974` / `stage=108` and disagrees with that `$v1`; those
fields are discarded. Same-run `[phase] cineState` via
`rdram_be32_at(0xB0934)` is boot garbage then 0 (83 zero rows from
6.0 s), including the last cinematic sample at 10.8 s.

## Conclusion

`H-PtrZeroSkip` is selected. `H-DtBelowThreshold`, `H-StageNeverHits7`,
and retry `H-CoverageInvalid` are refuted. Combined with s3306/s3307,
the port-only stop is that `0x800B0934` is 0 on every advancer call, so
the function always returns 0 and the 6074 gate never takes. dt `$a2`
is live (1/60 then 1/30), so the skip is the null pointer, not a
missing delta. The 600 s soak never published `$v0=1` either.

Named writer of `0x800B0934` is `cinematicInitializer` `sw` at
`0x800AF4B8`; named clearer is `cinematicDeactivator` `sw $zero` at
`0x800AF640`. Next discriminator is independent retail: who writes
physical `0x000B0934` during first attract, and whether that value is
a KSEG0 pointer.

Evidence dir: `scratch/agent/s3308_stage_advancer/`.
