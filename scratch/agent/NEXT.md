# NEXT work unit (s1995) — finalizeCurrentSpeechBuffer jal enter/exit

HYPOTHESIS-ID: hangar-frame-freeze

## What s1994 settled

Post-idle jals after `[drain-exit]`:
arbiter/destroy/shutdown nenter=1 nexit=1;
finalize nenter=1 nexit=0. 0 `[craft-select-s0]`.
H-later-drain-jal SELECTED site=
`finalizeCurrentSpeechBuffer`. H-arbiter-wait /
H-caller-returned / H-drain-exit-never-reached-again
REFUTED. Wrap control: the three prior sites both
edges printed. Recipe keeps
`ROGUESQ_DRAIN_INLOOP_TICK=0`.

finalize body (0x800678E4) is three jals:
always `shutdownMusyXVoices` (0x8009BCC4), then
`beq $a0, $zero` on `*(0x80139B74)` to either
`rs_free` or `teardownAssetDma`.

## Competing hypotheses

- **H-shutdown-musyx:** `shutdownMusyXVoices`
  nenter=1 nexit=0. Nested candidate inside it:
  the `lbu 0x80154620` / `bne $a0,$a1` spin at
  `L_8009BCEC` waiting for speech-slot byte 0.
- **H-rs-free:** shutdown exits; `$a0 != 0`;
  `rs_free` nenter=1 nexit=0.
- **H-teardown-dma:** shutdown exits; `$a0 == 0`;
  `teardownAssetDma` nenter=1 nexit=0.
- **H-finalize-body:** all taken jals nexit=1
  (or the skipped arm nenter=0) but finalize
  still nexit=0.

## Discriminating measurement (one instrument, one build, one 60s probe)

Named enter/exit counters on the three jals
inside `finalizeCurrentSpeechBuffer`. Log
`[fin-post] site=shutdown|free|teardown nenter=
nexit=` on each edge (first 8). Dump
`[fin-a0] a0=0x... beqz=N` once at
`0x800678FC` (the speech-buffer pointer).
If shutdown enters, also dump first 5 bytes of
`D_80154620` (`[fin-slot] b0=...`) — one line.

Keep `[drain-exit]` / `[drain-post]` /
`[drain-inloop-gate]` / `[craft-select-s0]`.
`S32`. No store changed. Do not default the
in-loop tick off.

Positive control: `[drain-inloop-gate] en=0`;
`[drain-exit] v0=1`; `[drain-post] site=finalize
nenter=1 nexit=0`; `[fin-post] site=shutdown
nenter=1` (first jal is unconditional).

Outcomes:
- shutdown nenter=1 nexit=0 → H-shutdown-musyx
  (`[fin-slot]` is the extra key)
- shutdown exits; free nenter=1 nexit=0 and
  a0!=0 → H-rs-free
- shutdown exits; teardown nenter=1 nexit=0
  and a0==0 → H-teardown-dma
- taken jals nexit=1 and finalize still
  nexit=0 → H-finalize-body

SENTINEL is applied — incremental edit, do not
rerun full fixup.

## Exact patch sites

- Incremental wrap of the three jals in
  `finalizeCurrentSpeechBuffer` (`funcs_15.c`)
  via `apply_s1995_finalize_post` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- One `[fin-a0]` at `beq 0x800678FC`; one
  `[fin-slot]` at shutdown enter.

## Exact test

```sh
mkdir -p scratch/agent/s1995_finalize_post
env ROGUESQ_DRAIN_INLOOP_TICK=0 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1995_finalize_post 60 2
```
