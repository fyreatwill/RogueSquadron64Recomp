# NEXT work unit (s2214) — distinguish host VI current-register publication timing

HYPOTHESIS-ID: m5-a1-port-current-reg-selector

## Work unit

Run the Rice-driven retail context preflight first, then add one opt-in
diagnostic timing arm to `lib/N64ModernRuntime/ultramodern/src/events.cpp`.
Keep `ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1` as the existing post-commit toggle
arm. Add `ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN=1` so the same host
register is toggled immediately before the VI thread enqueues its
`ScreenUpdateAction`; the new arm must not change the default or the existing
post-commit arm. Export the submodule patch and build once, then run control,
post-commit, and before-screen arms concurrently from that binary.

Competing hypotheses and the single discriminator:

- H-CommitToggle: the register must advance after `update_vi()` commits. The
  existing post-commit arm keeps the two target commits, while the
  before-screen arm changes the selected-field/committed-origin relationship.
- H-ScreenToggle: the register value must be advanced at screen publication.
  The before-screen arm preserves the retail target relation while the
  post-commit arm does not.
- H-TogglePlacementIrrelevant: both dynamic arms select field 0/1 and commit
  both target origins with the same bounded table; this closes timing as the
  discriminator but leaves the natural host publication source open.
- H-Coverage: the oracle control or any port arm lacks its positive prefix,
  width-640 rows, or zero-overflow table, so the comparison is unevaluable.

The one table is keyed by arm and committed 640 origin and records selected
field, current-line bit, commit count, candidate 0/1, phase origins, and
bounded context rows. Require the oracle whole-RDRAM control, joined retail
rows at both target origins with zero drops/overflow, one port prefix per arm,
512 width-640 rows per arm, and zero port overflow before classifying. Do not
enable either field arm by default. A matching pair of dynamic arms selects
H-TogglePlacementIrrelevant; only a stable divergence selects a timing
hypothesis.

## Exact commands

Retail ground truth, before the port edit:

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
  --press 6:start --hold-ms 200 > scratch/agent/s2214_retail_vi_reg_timing.log 2>&1
```

After adding the env-gated arm and exporting the patch, build once and run
all three arms concurrently:

```sh
./submodule-patches/export.sh
cmake --build build -j8
cd build
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 \
  ROGUESQ_VI_ALTERNATE_FIELDS=0 ROGUESQ_VI_FIELD_FROM_CURRENT_REG=0 \
  ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN=0 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2214_port_vi_reg_timing_control.log 2>&1 & p0=$!
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 \
  ROGUESQ_VI_ALTERNATE_FIELDS=0 ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1 \
  ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN=0 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2214_port_vi_reg_timing_commit.log 2>&1 & p1=$!
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 \
  ROGUESQ_VI_ALTERNATE_FIELDS=0 ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1 \
  ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN=1 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2214_port_vi_reg_timing_screen.log 2>&1 & p2=$!
for i in {1..60}; do
  alive=0
  for p in "$p0" "$p1" "$p2"; do
    kill -0 "$p" 2>/dev/null && alive=1
  done
  [ "$alive" -eq 0 ] && break
  sleep 1
done
kill -9 "$p0" "$p1" "$p2" 2>/dev/null || true
wait "$p0" "$p1" 2>/dev/null || true
wait "$p1" 2>/dev/null || true
wait "$p2" 2>/dev/null || true
cd ..
```

Inspect only the oracle control/context summary and the three port prefixes,
`[phase]` origin rows, `[vi-context-port]` selected field/current-line bits,
commit origins, summaries, overflow, and crash markers.
