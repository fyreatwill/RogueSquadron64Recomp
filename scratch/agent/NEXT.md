# NEXT work unit (s2054)

HYPOTHESIS-ID: m5-lle-mode-causality

## Work unit

Run the retail oracle first with its whole-RDRAM positive control and the
title/hangar VI trace. Then run one four-arm port table concurrently from the
same existing build and the same qualified recipe. Keep forced LLE, C88=1,
opt-in audio, spin yield, the eleven width-640 Starts, the dense post-title
schedule, and all passive diagnostics fixed. Vary only
`ROGUESQ_LLE_UNGATED` and `ROGUESQ_LLE_SOLO` across `11`, `10`, `01`, and
`00`. Do not change the guest writer, callback, AI shortcut, or any guard.

## Competing hypotheses and discriminator

- **H-U — UNGATED is causal:** arms `11` and `10` reach the phase-valid title
  VI 1024 and hangar VI 512 chain; `01` and `00` do not.
- **H-S — SOLO is causal:** arms `11` and `01` reach both anchors; `10` and
  `00` do not.
- **H-I — the flags interact:** only arm `11` reaches hangar VI 512.
- **H-N — neither flag is causal:** all four arms have the same phase result;
  an irregular table means the route recipe is still unstable rather than
  selecting a flag.

The single discriminator is the four-row phase-keyed table of preflight,
`menuControllerInput`/`menuInput`, VI 1024 at `0x00790400`, and VI 512 at
`0x006AB400`, with missing-function/deferred-drop/abort controls. A late
width-640 key warning after a valid 512 transition is only a recipe-quality
warning and does not invalidate that arm's target chain.

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
  > scratch/agent/s2054_oracle.log 2>&1

set +e
route_keys='640@6:start 640@11:start 640@16:start 640@21:start 640@26:start 640@31:start 640@36:start 640@41:start 640@46:start 640@51:start 640@56:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a'

run_arm() {
  arm_label="$1"
  ungated="$2"
  solo="$3"
  env REGRESS_SECS=90 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL="$arm_label" \
    ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED="$ungated" ROGUESQ_LLE_SOLO="$solo" \
    ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
    ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 \
    ROGUESQ_LOG_M5_CALLER_EDGE=1 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
    ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_VI_TRANSITION=1 \
    ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 \
    ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_PCM_SANITY=1 \
    zsh tools/regress.sh "scratch/agent/$arm_label" 90 \
    > "scratch/agent/${arm_label}_driver.log" 2>&1
}

run_arm s2054_lle_11 1 1 &
run_arm s2054_lle_10 1 0 &
run_arm s2054_lle_01 0 1 &
run_arm s2054_lle_00 0 0 &
wait
```

Inspect only each `verdict.json`, preflight/phase lines, target marker counts,
and log tails. Report the four-row table before selecting H-U, H-S, H-I, or
H-N.
