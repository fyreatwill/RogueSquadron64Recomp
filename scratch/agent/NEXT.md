# NEXT work unit (s2219) — test the existing C88 gate writer arm

HYPOTHESIS-ID: m5-audio-gate-writer-site

## Work unit

Execute M5 plan step 3 for exactly one writer: `reapplyDisplayMode`'s gate
store at guest `0x8008EC88`. Ask the retail oracle for the store payload and
writer attribution first. Only after its whole-RDRAM control is positive, run
one same-build port A/B with the Factor 5 image arm held constant and the
existing `ROGUESQ_M5_C88_VALUE=1` behavior arm versus the default forced-zero
control. Do not change any other gate writer, consumer, task field, default,
or safety guard.

Competing hypotheses and the single discriminator:

- H-C88RetailOne: retail writes `1` at this site in the target route and the
  port's original-value arm changes the gate contract; the arm should show a
  phase-keyed gate transition plus a downstream task/slot/PCM difference.
- H-C88RetailZero: retail writes `0` at this site in the covered target
  route; the port's forced-zero control matches retail and the A/B has no
  downstream difference.
- H-C88NotCausal: retail and port payloads match, but this writer is not the
  missing boundary; task exit, validated slot completion, and PCM remain
  matched between arms.
- H-C88RouteRegress: changing only this writer alters route admission or
  stability while the positive prefix is present, without establishing a
  valid audio result.

The discriminator is one joined table containing the oracle whole-RDRAM
control, gate writer PC and post-store value, port gate rows at the writer
site, positive 640/title/hangar phases, image-arm `real_ucode`/exit rows,
nonzero PCM joins, and an independently validated slot-status transition.
Missing whole-RDRAM or phase controls makes the comparison unevaluable;
writer counts alone do not select a hypothesis.

## Ground-truth command — run before any port build or new instrumentation

~~~sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 60 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --watch-write 0x0:0x800000 \
  --watch-write 0xA0F50:0xA0F51 \
  --pc-hist-watch 1 --post-value-watch 1 \
  --post-value-pc 0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ED48 \
  > scratch/agent/s2220_retail_c88.log 2>&1
~~~

The whole-RDRAM watch must reach its positive-control threshold and the Rice
trace must reach both target 640 origins and the hangar before a zero payload
or missing writer is interpreted.

## Port build and same-build A/B

~~~sh
cmake --build build --config Debug --target RogueSquadron64Recomp
~~~

Run both arms concurrently, holding the image arm constant and arming all
passive M5 diagnostics:

~~~sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 \
  ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 \
  ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-c88-on 30 12 \
  > scratch/agent/s2220_c88_on.log 2>&1

env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 \
  ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 \
  ROGUESQ_LOG_AUDIOTICK_TRACE=1 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-c88-control 30 12 \
  > scratch/agent/s2220_c88_control.log 2>&1
~~~

Use SIGKILL for watchdog cleanup. Do not promote `ROGUESQ_M5_C88_VALUE=1`
based on a route or dispatch change without the oracle payload and valid
slot/PCM evidence.
