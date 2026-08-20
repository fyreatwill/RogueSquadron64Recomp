# NEXT work unit (s2051)

HYPOTHESIS-ID: m5-route-requalification

## Work unit

Run the retail oracle first with its whole-RDRAM positive control and the
title/hangar VI trace. Then run a same-build, sequential spin-yield A/B with
C88 fixed at `1`, using the eleven width-640 Starts and the dense post-title
schedule. Sequential launch preserves the GUI focus that the failed
concurrent pair did not. Keep the opt-in audio arm and every passive control.
The new discriminator is whether the known-good title route is reproducible
and whether the spin arm visibly fires its positive control. Do not start the
C88 polarity comparison until one arm reaches VI 1024.

## Competing hypotheses and discriminator

- **Q1 — scheduler route is active but transient:** the yield-on arm emits
  `[spin-yield]` and reaches title VI 1024, while the yield-off arm remains
  at VI 640. The title route is restored; C88 qualification becomes admissible.
- **Q2 — current 640 boundary is deterministic guest/menu state:** both arms
  have `[pad-host]` and caller/post-wait controls but no VI 1024. The issue is
  upstream of C88 and needs a new route probe.
- **Q3 — the spin arm is not active in the binary/config:** neither arm emits
  `[spin-yield]`, even if one reaches 1024. Check the build/config provenance
  before interpreting route depth.
- **Q4 — GUI/input failure:** an arm lacks `input=ok visual=ok` or host Start
  rises. Discard its route result and request an active desktop run.

The single discriminator is the two-arm table of preflight, `[pad-sdl]`,
`[pad-host]`, `[spin-yield]`, caller/post-wait controls, VI 1024/512, and
`menuControllerInput`. PCM and bridge rows remain inadmissible without both
target VI anchors.

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
  > scratch/agent/s2051_oracle.log 2>&1

set +e
route_keys='640@6:start 640@11:start 640@16:start 640@21:start 640@26:start 640@31:start 640@36:start 640@41:start 640@46:start 640@51:start 640@56:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a'
common_env=(REGRESS_SECS=130 REGRESS_INTERVAL=0.6 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_CALLER_EDGE=1 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_VI_TRANSITION=1 ROGUESQ_LOG_PCM_SANITY=1)
env $common_env REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2051_spin_on ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 zsh tools/regress.sh scratch/agent/s2051_spin_on 130 > scratch/agent/s2051_spin_on_driver.log 2>&1
rc_on=$?
env $common_env REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2051_spin_off ROGUESQ_M5_C88_VALUE=1 zsh tools/regress.sh scratch/agent/s2051_spin_off 130 > scratch/agent/s2051_spin_off_driver.log 2>&1
rc_off=$?
printf 'spin_on_rc=%s spin_off_rc=%s\n' "$rc_on" "$rc_off"
```

Confirm the binary contains `ROGUESQ_SPIN_YIELD` before running. Inspect only
each `verdict.json`, `env.txt`, bounded tag counts, and log tails; do not read
a full run log.
