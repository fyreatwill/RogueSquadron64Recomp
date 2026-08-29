# NEXT work unit — qualify Step 6 drain-tick policy with a game run

HYPOTHESIS-ID: m5-audio-destub-step6-policy

## Resume context

Session 3152 built the centralized `rs64_m5_apply_drain_tick_policy()` startup
helper successfully.  H-Step6-BuildRegression was REFUTED.  The built binary is
at `build/RogueSquadron64Recomp`.  The fixup's `apply_s1993_drain_inloop_gate()`
was verified correct in situ (already uses `*e == '1'`); no fixup edit was made.

Two hypotheses remain open — they require a game run:
- `H-Step6-PolicyApplied`: default launch (no env override) logs
  `[drain-inloop-gate] en=0`; ROGUESQ_DRAIN_INLOOP_TICK=1 logs `en=1`.
- `H-Step6-PolicyBypassed`: default launch still logs `en=1` (policy not
  applied before the first drain call, or env read too late).

## Single work unit

Run the built binary twice from `build/` with the ROM present:
1. Default (no ROGUESQ_DRAIN_INLOOP_TICK): capture stderr; check for
   `[drain-inloop-gate] en=0`.
2. With `env ROGUESQ_DRAIN_INLOOP_TICK=1 ./RogueSquadron64Recomp`: check for
   `[drain-inloop-gate] en=1`.

Both arms must produce the gate line (positive control) before any audio
conclusion is drawn.  A missing gate line means the drain code path was not
reached before the crash window — note it but do not infer policy state.

Do NOT rebuild unless the binary is missing.  Kill runs with SIGKILL after
≤60s.  Run from `build/` with the ROM present.

## Exact commands

```sh
ls build/RogueSquadron64Recomp
cd build
./RogueSquadron64Recomp 2>&1 | tee /tmp/rs64_default.log &
GAME_PID=$!; sleep 30; kill -9 $GAME_PID 2>/dev/null
grep 'drain-inloop-gate' /tmp/rs64_default.log

env ROGUESQ_DRAIN_INLOOP_TICK=1 ./RogueSquadron64Recomp 2>&1 | tee /tmp/rs64_explicit.log &
GAME_PID=$!; sleep 30; kill -9 $GAME_PID 2>/dev/null
grep 'drain-inloop-gate' /tmp/rs64_explicit.log
```

## Discriminating outcomes

| Outcome | Selects |
|---|---|
| default=`en=0`, explicit=`en=1` | H-Step6-PolicyApplied — proceed to Step 6 full validation |
| default=`en=1` regardless | H-Step6-PolicyBypassed — diagnose env timing or getenv order |
| gate line absent in both | gate not reached; note path, pick next M5 step |
