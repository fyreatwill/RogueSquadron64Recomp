# NEXT work unit (s2216) — measure callback versus retrace parity at skipped host VIs

HYPOTHESIS-ID: m5-a1-natural-current-reg-publication

## Work unit

Run the Rice-driven retail preflight first. Then add one opt-in scheduler table
to `lib/N64ModernRuntime/ultramodern/src/events.cpp`, gated by
`ROGUESQ_LOG_VI_PARITY_SCHEDULER=1`. For the first 512 game-started width-640
VI callbacks, record callback ordinal, `total_vis`, delta from the previous
`total_vis`, selected field, current-line bit, and committed origin; summarize
the count of `delta_total_vis > 1` rows and the origin/field mapping. Do not
change VI behavior in this unit. Export the submodule patch and build once;
run control, existing post-commit current-register, and the s2215
retrace-parity arm concurrently from that binary.

Competing hypotheses and the single discriminator:

- H-RetraceParity: after a skipped host VI, `total_vis & 1` is the parity that
  follows the retail origin/field relation; the retrace-parity arm agrees with
  the total-vis bit while the per-callback arm diverges.
- H-PerCallbackToggle: field advances are tied to delivered VI callbacks; on
  rows with `delta_total_vis > 1`, the post-commit arm's callback parity agrees
  with retail while total-vis parity diverges.
- H-NoSkippedVI: no width-640 row has `delta_total_vis > 1`, so this run cannot
  distinguish the two cadence hypotheses and must leave the publisher open.
- H-Coverage: the scheduler table lacks its positive prefix, 512 width-640
  rows, or has overflow/crash markers, so the comparison is unevaluable.

The one table is keyed by arm and committed 640 origin and records callback
ordinal, `total_vis`, delta, selected field, current-line bit, and commit
origin. Require the retail whole-RDRAM control, joined retail rows at both
target origins with zero drops/overflow, one port prefix per arm, 512
width-640 rows per arm, zero port overflow, and an explicit skipped-VI count.
Classify only from the same-run table. Do not enable any diagnostic arm by
default.

## Exact commands

Retail ground truth, before the port edit:

~~~
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
  --press 6:start --hold-ms 200 > scratch/agent/s2216_retail_vi_parity_scheduler.log 2>&1
~~~

After the table is added and exported, build once and run all three arms
concurrently:

~~~
./submodule-patches/export.sh
cmake --build build -j8
cd build
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 \
  ROGUESQ_LOG_VI_PARITY_SCHEDULER=1 \
  ROGUESQ_VI_ALTERNATE_FIELDS=0 ROGUESQ_VI_FIELD_FROM_CURRENT_REG=0 \
  ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN=0 \
  ROGUESQ_VI_CURRENT_REG_FROM_TOTAL_VIS=0 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2216_port_vi_parity_scheduler_control.log 2>&1 & p0=$!
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 \
  ROGUESQ_LOG_VI_PARITY_SCHEDULER=1 \
  ROGUESQ_VI_ALTERNATE_FIELDS=0 ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1 \
  ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN=0 \
  ROGUESQ_VI_CURRENT_REG_FROM_TOTAL_VIS=0 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2216_port_vi_parity_scheduler_commit.log 2>&1 & p1=$!
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 \
  ROGUESQ_LOG_VI_PARITY_SCHEDULER=1 \
  ROGUESQ_VI_ALTERNATE_FIELDS=0 ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1 \
  ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN=0 \
  ROGUESQ_VI_CURRENT_REG_FROM_TOTAL_VIS=1 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2216_port_vi_parity_scheduler_total_vis.log 2>&1 & p2=$!
for i in {1..60}; do
  alive=0
  for p in "$p0" "$p1" "$p2"; do
    kill -0 "$p" 2>/dev/null && alive=1
  done
  [ "$alive" -eq 0 ] && break
  sleep 1
done
kill -9 "$p0" "$p1" "$p2" 2>/dev/null || true
wait "$p0" 2>/dev/null || true
wait "$p1" 2>/dev/null || true
wait "$p2" 2>/dev/null || true
cd ..
~~~

Inspect only each positive prefix, scheduler-table rows/summary, `[phase]`
origin rows, `[vi-context-port]` selected-field/current-line rows, commit
origins, overflow, and crash markers.
