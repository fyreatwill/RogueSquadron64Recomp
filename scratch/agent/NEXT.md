# NEXT work unit (s2213) — test the host VI current-register selector

HYPOTHESIS-ID: m5-a1-port-current-reg-selector

## Work unit

Run the retail context-table preflight first, then make one opt-in diagnostic
arm in `lib/N64ModernRuntime/ultramodern/src/events.cpp`. The arm should use
`regs.VI_V_CURRENT_LINE_REG & 1` as the `ViState::update_vi` field selector
and toggle that host register after each VI commit. Keep the existing
`ROGUESQ_VI_ALTERNATE_FIELDS=1` arm unchanged as a comparison; the new arm is
not a default change and is not a mitigation.

Competing hypotheses and the single discriminator:

- H-CurrentRegIsTheSelector: the independent retail context table shows
  `VI_CURRENT_REG & 1` alternating with the next origin, and the new port arm
  selects field 0/1 from the register and commits both early/target origins.
- H-CurrentRegPortContractMissing: retail alternates, but the port current-reg
  arm does not reproduce the existing alternate arm's selected-field/current-
  line/commit relationship. The missing work is the host VI register contract,
  not the mode descriptor or a guest writer.
- H-CurrentRegRecoveryOnly: the new arm and the existing field-alternation arm
  produce the same two-origin recovery, but the synthetic host toggle cannot
  identify retail provenance. This closes the port recovery path while leaving
  the retail-to-port current-register publication boundary open.
- H-CurrentRegCoverage: the oracle positive control fires, but the context join
  or one or more port arms lacks a positive prefix, a width-640 row, or has
  row overflow. The run is unevaluable and selects no source hypothesis.

The one table is keyed by arm and committed 640 origin and records selected
field, pre-commit `VI_V_CURRENT_LINE_REG & 1`, commit count, candidate 0/1,
and the bounded context rows. Require the oracle whole-RDRAM control, at least
one joined retail context row at each target origin, one port prefix row, one
width-640 row per arm, and zero port overflow before classifying. Compare the
new arm with the existing alternate arm and with retail's
`current_field=0`/`1` context rows. Do not enable either field arm by default.

## Exact commands

Retail ground truth, before the port edit/build:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --rsp /opt/homebrew/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --input /opt/homebrew/lib/mupen64plus/mupen64plus-input-sdl.dylib \
  --secs 10 --hit-cap 10000 --watch-write 0:0x800000 \
  --watch-pc 0x80035550 --vi-context-table-pc 0x80035550 \
  --pc-phase-log 0x0066A500 --pc-phase-log 0x005D4500 \
  --pc-phase-log 0x0066AA00 --pc-phase-log 0x00696100 \
  --pc-phase-log 0x00696600 --vi-trace \
  --press 6:start --hold-ms 200 > scratch/agent/s2213_retail_current_reg.log 2>&1
```

Then add the env-gated arm, export, build once, and run all three arms from
the same build concurrently:

```sh
./submodule-patches/export.sh
cmake --build build -j8
cd build
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_VI_CONTEXT_PORT=1 ROGUESQ_VI_ALTERNATE_FIELDS=0 \
  ROGUESQ_VI_FIELD_FROM_CURRENT_REG=0 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2213_port_current_reg_control.log 2>&1 & p0=$!
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_VI_CONTEXT_PORT=1 ROGUESQ_VI_ALTERNATE_FIELDS=1 \
  ROGUESQ_VI_FIELD_FROM_CURRENT_REG=0 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2213_port_current_reg_alternate.log 2>&1 & p1=$!
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_VI_CONTEXT_PORT=1 ROGUESQ_VI_ALTERNATE_FIELDS=0 \
  ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2213_port_current_reg_selector.log 2>&1 & p2=$!
for i in {1..60}; do
  alive=0
  for p in "$p0" "$p1" "$p2"; do
    kill -0 "$p" 2>/dev/null && alive=1
  done
  [ "$alive" -eq 0 ] && break
  sleep 1
done
kill -9 "$p0" "$p1" "$p2" 2>/dev/null || true
wait "$p0" "$p1" "$p2" 2>/dev/null || true
cd ..
```

Inspect only the oracle positive-control/context summary and the three port
prefixes, `[phase]` origin rows, context summaries, selected field/current
line bits, commit origins, and overflow/crash markers. If all controls pass
and all three tables are non-overflowing, classify exactly one hypothesis.
