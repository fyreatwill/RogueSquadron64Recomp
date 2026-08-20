# NEXT work unit (s2050)

HYPOTHESIS-ID: m5-guest-gate-causality

## Work unit

Run the retail oracle first with the whole-RDRAM positive control and the
existing title/hangar VI trace. Then run both arms of one phase-gated route
qualification from the existing build: explicit `ROGUESQ_M5_C88_VALUE=1` and
the variable unset. Keep forced LLE, opt-in audio, spin yield, the eleven
boot-relative width-640 Starts, the dense post-title schedule, and every
passive control in both arms. Treat an arm as valid only if it has
`input=ok visual=ok`, `[pad-sdl]` key rows, `[pad-host]` rows, title VI 1024,
and the caller/gate/service controls. Compare only VI transitions, not wall
clock. Do not interpret bridge or PCM unless that arm also reaches VI 512.

## Competing hypotheses and discriminator

- **G1 — explicit C88=1 is the route gate:** the unset arm reaches
  `menuControllerInput` and VI 512 while the explicit-1 arm reproduces the
  title-only R2 boundary.
- **G2 — opposite value polarity:** explicit C88=1 reaches the menu/512
  route while the unset arm stops at title.
- **G3 — C88 is not causal:** both valid arms have the same depth, especially
  title VI 1024 with no `menuControllerInput` and no VI 512.
- **G4 — recipe/focus failure:** either arm lacks the preflight or input
  positive controls, so its route result is discarded and the recipe is
  repaired rather than compared.

The single discriminator is one arm-by-arm table keyed by preflight,
`[pad-sdl]`/`[pad-host]`, VI 1024/512 anchors, `menuControllerInput`, caller
edges, VI-producer requests, and service controls. G1 wins when only unset
has both menu input and 512; G2 when only explicit 1 does; G3 when both valid
arms stop at the same depth; G4 when a positive control is missing. PCM is
inadmissible for any arm without both target anchors.

## Commands

```sh
# Ground truth first.
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 --watch-write 0x0:0x800000 \
  --watch-pc 0x800C28F0,0x800B47D0,0x8008E57C --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2050_oracle.log 2>&1

set +e
route_keys='640@6:start 640@11:start 640@16:start 640@21:start 640@26:start 640@31:start 640@36:start 640@41:start 640@46:start 640@51:start 640@56:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a'
common_env=(REGRESS_SECS=130 REGRESS_INTERVAL=0.6 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_CALLER_EDGE=1 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_VI_TRANSITION=1 ROGUESQ_LOG_PCM_SANITY=1)
env $common_env REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2050_c88_one ROGUESQ_M5_C88_VALUE=1 zsh tools/regress.sh scratch/agent/s2050_c88_one 130 > scratch/agent/s2050_c88_one_driver.log 2>&1 &
pid_one=$!
env -u ROGUESQ_M5_C88_VALUE $common_env REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2050_c88_unset zsh tools/regress.sh scratch/agent/s2050_c88_unset 130 > scratch/agent/s2050_c88_unset_driver.log 2>&1 &
pid_unset=$!
wait "$pid_one"; rc_one=$?
wait "$pid_unset"; rc_unset=$?
printf 'c88_one_rc=%s c88_unset_rc=%s\n' "$rc_one" "$rc_unset"
```

Inspect only each `verdict.json`, `env.txt`, bounded tag counts, and log
tails. Do not read a full run log or treat a final-key scorer failure as a
route verdict when the arm has its phase and input controls.
