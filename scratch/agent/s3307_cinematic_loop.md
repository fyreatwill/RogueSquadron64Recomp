# Session 3307 — port cinematicLoopBody loops; exit-gate $v0 stays 0 through 120 s

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

## Competing hypotheses

- `H-PortPrologueStall`: entry fires; `0x800A5DD8` is `$v0=1` or
  silent; loop-head `0x800A6024` never runs.
- `H-PortLoopNoExit`: loop-head and backedge are live; `0x800A6074`
  stays `$v0=0`; `0x800A64BC` / `0x800A6618` stay silent through 120 s.
- `H-PortExitNoReturn`: `0x800A6074` `$v0=1` and `0x800A64BC` fire;
  `0x800A6618` / `0x8003E114` stay silent.
- `H-CoverageInvalid`: missing viewer-return, cinematic-entry, VI-640,
  SP-completion, or mark-all control.

## What ran

One regeneration-safe table covering the seven internal edges plus the
existing s3305 entry/return. Live apply:
`tools/apply_s3306_cinematic_loop.py` into `funcs_27.c`. The same
transform is imported by `N64Recomp/fixup_game_funcs.py`. Diagnostic
only: no guest store/branch change, no M5 Step 3.

The first launch (`run1_crash.log`) died at 6 s with
`spTaskSchedulerThread` SIGSEGV at VI 320 (`last-guest-pc=0x8000834c`,
`si_addr=0x400128d47`) before any mark-all or cinematic row. That run
is coverage-invalid. The same-binary retry (`run.log`, 121 s watchdog)
is the live scope. Driver: `scratch/agent/s3307_cinematic_loop/run.sh`.

No skip, allow, restore, wait bypass, or audio/output change.

## Same-run positive controls (121 s retry)

- `[s3306-cine-loop-control] mark` IDs 0–6 (7/7).
- `[s3305-postviewer-control] mark` IDs 0–23 (24/24).
- `arm=completion-wins-default` 69 rows; `requested_pre=1 requested_post=0` 69.
- `[event-wiring] complete kind=SP` 64 rows.
- `[phase] vi_width=640 (was 320) origin=0x0066A500` at 3.1 s `#104`.
- Viewer `[m5-postwait]` entry and return.
- s3305 cinematic-call / cinematic-entry (`$a0=0x13`) at origin `0x66A500`.
- Zero `[CRASH]` / `[ABORT]` on the retry.

## Port first-attract cinematic (live retry)

| n | site | `$v0` | taken | origin | VI # |
|---|---|---|---|---|---:|
| 1 | early-exit `0x800A5DD8` | **1** | 0 | `0x66A500` | 320 |
| 1 | loop-head `0x800A6024` | `0x80140000` | 0 | `0x696100` | 384 |
| 1–150 | exit-gate `0x800A6074` | **0** | 0 | `0x696100` | 384–640 |
| 1–150 | backedge `0x800A64B4` | 1 | 0 | `0x696100`/`0x62BD00` | 384–640 |

Lifetime printed (first 8, then every 50): `5DD8=1`, `6024=11`,
`6074=11` all `$v0=0` `v0_nz=0`, `64B4=11`. Silent: `64BC`, `65E4`,
`6618`, s3305 edge 20/21/22, title 1024. Last VI `#704` still
`640 @ 0x0062BD00`. Last printed loop n=150 at VI `#640`; n=200 was
not reached before SIGKILL (rate-limit hides 151–199).

Early-exit `$v0=1` not taken matches retail s3306. First loop-head
`$v0=0x80140000` matches retail's prologue fall-through. The port
then stays in the backedge with exit-gate `$v0=0` for the whole
bounded run. Retail took `$v0=1` at 48.8 s after 1002 gate visits.

## Conclusion

`H-PortLoopNoExit` is selected. `H-PortPrologueStall`,
`H-PortExitNoReturn`, and retry `H-CoverageInvalid` are refuted.
Combined with retail Session 3306, the port-only stop is that
`cinematicStageAdvancer`'s `$v0` never becomes 1 on this 120 s
window: either the skip/stage/dt predicate is stuck, or the port
is iterating too slowly to reach retail's ~1003-iter exit. No M5
Step 3. Evidence dir: `scratch/agent/s3307_cinematic_loop/`.
