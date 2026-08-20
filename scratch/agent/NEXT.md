# NEXT work unit (s2060)

HYPOTHESIS-ID: m5-guest-gate-handoff

## Work unit

Run the retail oracle first, then add one opt-in `REGRESS_NO_FOCUS=1` branch
to `tools/regress.sh` that skips only the `raise_game` call. Run both C88 arms
with that branch in the same iteration. `winctl key` already posts directly to
the game PID, so this tests whether the prior menu callback-count difference
depends on the harness raising the window rather than on the guest gate.

Do not change `0x8008EC88`, the retail writer, any guest status byte, audio
task behavior, menu code, or the scorer. Keep the existing qualified
forced-LLE/audio/spin-yield route and the existing post-wait, input, gate,
menu, audio-task/ABI, and PCM controls.

## Competing hypotheses and discriminator

- **H-Focus** — skipping `raise_game` prevents the scheduled keys from being
  observed. The no-focus arms will miss `[pad-host]` in the target phases or
  fail title VI 1024/hangar VI 512, so the earlier callback difference cannot
  be attributed to C88 until input delivery is repaired.
- **H-GateRoute** — direct PID input remains live without a focused window in
  both arms, and both reach the two target VIs, but C88=1 still takes the
  active raw-gate branch and has the larger `menuControllerInput`/`menuInput`
  count. This selects the guest gate/route as the cause at this scope and
  refutes GUI focus.
- **H-StateOnly** — direct input and both target VIs remain live, but the
  callback counts converge while the oracle's menu-state watch and the port's
  post-wait branch rows remain different. This would move the discriminator
  from focus to a guest menu-state boundary without changing C88.
- **H-RetailMismatch** — the oracle positive controls fire but its watched
  menu PCs/state writes do not cover the driven title-to-hangar route. The
  retail witness is then insufficient for this question; do not infer a port
  callback explanation from the A/B rows.

The selecting table is phase-keyed: preflight input/visual, retail whole-RDRAM
positive control, retail title/hangar VIs, port title VI 1024, port hangar VI
512, `[pad-host]` in both target phases, raw-gate branch/value, the
`menuControllerInput`/`menuInput` callback counts, and the existing
post-wait/ABI/PCM controls. H-Focus requires the no-focus input/route controls
to fail. H-GateRoute requires both arms' direct-input/route controls plus a
non-convergent callback/gate table. H-StateOnly requires live input/route
controls with convergent callbacks but divergent state/branch rows.

## Ground truth command (run before editing the harness)

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x0CE730:0x0CE828 \
  --watch-pc 0x800B47C4,0x800B8014,0x800B8050 \
  --vi-trace --pif-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start \
  > scratch/agent/s2060_oracle.log 2>&1
```

Require the whole-RDRAM control to reach its threshold, title VI 1024 and
hangar VI 512, PIF input rows, and at least one relevant menu PC/state row
before treating a retail null as evidence.

## Harness change and port arms

Add this bounded branch around the existing `raise_game` invocation in
`tools/regress.sh`:

```sh
if [[ -z "${REGRESS_NO_FOCUS:-}" ]]; then
    raise_game
else
    print "focus: skipped window raise; keys use direct PID injection"
fi
```

Then run both arms sequentially with the same route and no 512-phase input:

```sh
route_keys='640@6:start 640@11:start 640@16:start 640@21:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a'
env REGRESS_REQUIRE_VISUAL=1 REGRESS_SECS=180 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2060_no_focus_c88_on \
  REGRESS_NO_FOCUS=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_POSTWAIT=1 \
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2060_no_focus_c88_on 180 \
  > scratch/agent/s2060_no_focus_c88_on_driver.log 2>&1

env -u ROGUESQ_M5_C88_VALUE REGRESS_REQUIRE_VISUAL=1 REGRESS_SECS=180 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2060_no_focus_c88_unset \
  REGRESS_NO_FOCUS=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_POSTWAIT=1 \
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2060_no_focus_c88_unset 180 \
  > scratch/agent/s2060_no_focus_c88_unset_driver.log 2>&1
```

ORIGIN: no guest writer, value, wait, guard, skip, audio task, callback, or
default behavior change is authorized; the only harness change is an opt-in
skip of window raising while retaining direct PID key injection.
