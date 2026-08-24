# NEXT work unit (s2215) — test retrace-parity as the natural current-register publisher

HYPOTHESIS-ID: m5-a1-natural-current-reg-publication

## Work unit

Run the Rice-driven retail preflight first, then add one opt-in diagnostic arm
to lib/N64ModernRuntime/ultramodern/src/events.cpp:
ROGUESQ_VI_CURRENT_REG_FROM_TOTAL_VIS=1. When combined with the existing
ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1, publish total_vis & 1 to
VI_V_CURRENT_LINE_REG immediately before the screen action is enqueued, and
do not apply either synthetic XOR toggle in that arm. Keep the default, the
existing post-commit current-register arm, and the before-screen timing arm
unchanged. Export the submodule patch and build once; run control, existing
post-commit, and retrace-parity arms concurrently from that binary.

Competing hypotheses and the single discriminator:

- H-RetraceParity: the host's retrace ordinal is the omitted publication
  source. The retrace-parity arm selects the retail-matching field at both
  target origins and reproduces the existing dynamic arm's early-origin
  relation in the same bounded table.
- H-PerCallbackToggle: the port needs one field advance per delivered VI
  callback, not absolute retrace parity. The retrace-parity arm diverges from
  the existing post-commit arm in selected field or committed target origin,
  especially after a skipped host VI.
- H-FieldState: the current register is not the natural source; the table's
  target result is unchanged only because both synthetic arms are equivalent,
  while the default vi.field arm remains field 0. This keeps the publisher open
  and authorizes no default flip.
- H-Coverage: any arm lacks its positive prefix, 512 width-640 rows, or has
  overflow/crash markers, so the comparison is unevaluable.

The one table is keyed by arm and committed 640 origin and records selected
field, current-line bit, candidate 0/1, early and target phase origins,
commit counts, and bounded context rows. Require the retail whole-RDRAM
control, joined retail rows at both target origins with zero drops/overflow,
one port prefix per arm, 512 width-640 rows per arm, and zero port overflow.
Classify only from the same-run table. Do not enable the new arm by default.

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
  --press 6:start --hold-ms 200 > scratch/agent/s2215_retail_current_reg_retrace.log 2>&1
~~~

After the env-gated arm is added and exported, build once and run all three
arms concurrently:

~~~
./submodule-patches/export.sh
cmake --build build -j8
cd build
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 \
  ROGUESQ_VI_ALTERNATE_FIELDS=0 ROGUESQ_VI_FIELD_FROM_CURRENT_REG=0 \
  ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN=0 \
  ROGUESQ_VI_CURRENT_REG_FROM_TOTAL_VIS=0 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2215_port_current_reg_retrace_control.log 2>&1 & p0=$!
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 \
  ROGUESQ_VI_ALTERNATE_FIELDS=0 ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1 \
  ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN=0 \
  ROGUESQ_VI_CURRENT_REG_FROM_TOTAL_VIS=0 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2215_port_current_reg_retrace_commit.log 2>&1 & p1=$!
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 \
  ROGUESQ_VI_ALTERNATE_FIELDS=0 ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1 \
  ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN=0 \
  ROGUESQ_VI_CURRENT_REG_FROM_TOTAL_VIS=1 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2215_port_current_reg_retrace_total_vis.log 2>&1 & p2=$!
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

Inspect only each positive prefix, [phase] origin rows, the
[vi-context-port] selected-field/current-line rows, commit origins,
summary, overflow, and crash markers.
