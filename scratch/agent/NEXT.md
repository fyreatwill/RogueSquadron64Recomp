# NEXT work unit (s2221) — audit the key-on divide/return class

HYPOTHESIS-ID: m5-audio-keyon-contract

## Work unit

Execute M5 plan step 4 as one bounded census of the existing eight
`musyxKeyOnVoice` divide/overflow return sites. Keep the C88 `=1` behavior arm
and Factor 5 image arm constant; do not remove or rewrite a return in this
iteration. Use the already-generated `ROGUESQ_LOG_M5_KEYON_CENSUS` table and
the named slot probes, with the retail oracle's whole-RDRAM positive control
and target-phase coverage captured before interpreting any null.

Competing hypotheses and the single discriminator:

- H-KeyOnValidNormal: the C88-enabled route supplies valid key-on inputs;
  divide witnesses have nonzero/in-range operands, the normal tail runs, and
  the named slot writer shows `0x02 -> 0x00` after the key-on chain.
- H-KeyOnGuardNeeded: at least one divide site sees an invalid divisor or
  pointer/range, and the current early return is exercised; normal-tail and
  terminal-slot evidence remains absent for that record.
- H-KeyOnRouteOnly: C88 reaches hangar and nonzero PCM, but key-on entries do
  not causally produce the observed slot/PCM transitions; the census remains
  phase-mismatched or all key-on records are outside the target window.
- H-KeyOnCoverageFailure: the positive phase and key-on controls do not cover
  hangar, so no return-site conclusion is evaluable.

The discriminator is one phase-keyed table joining oracle whole-RDRAM and
Rice target-phase controls, port key-on entry/divide-witness/guard/normal-tail
rows for all eight sites, valid operand/range fields, named slot transitions,
hangar phase, and nonzero PCM joins. Do not promote a guard removal from an
entry count or a slot writer count alone.

## Ground-truth command — run before any port build or new instrumentation

~~~sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 60 --vi-trace --status-poll \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x80090A3C,0x80090CEC,0x80090D04,0x80090D30,0x80090D48,0x80090D74,0x80090D8C,0x80090DB8,0x80090DD0,0x80090DE8 \
  --hit-cap 200 \
  > scratch/agent/s2221_retail_keyon.log 2>&1
~~~

The whole-RDRAM watch must reach its positive-control threshold and the Rice
trace must reach both target 640 origins and hangar before a zero key-on or
missing execution is interpreted. If a new oracle watch is needed for a
specific operand, add it only after this preflight and keep the whole-RDRAM
control in the same run.

## Port build and census

~~~sh
cmake --build build --config Debug --target RogueSquadron64Recomp
~~~

Run the C88-enabled arm from the existing mission-key schedule, holding the
image arm constant and arming all passive M5 diagnostics plus the existing
key-on census:

~~~sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 \
  ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 \
  ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 \
  ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_VI_CALLERS=1 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-keyon-census 30 12 \
  > scratch/agent/s2221_keyon_census.log 2>&1
~~~

Use SIGKILL for watchdog cleanup. Expected outcomes: H-KeyOnValidNormal
requires divide witnesses with valid operands, normal-tail rows, and named
slot/PCM transitions in hangar; H-KeyOnGuardNeeded requires a concrete invalid
operand at a named site; H-KeyOnRouteOnly or H-KeyOnCoverageFailure leaves the
key-on class parked and changes no generated behavior. No default, gate,
task-field, safety-guard, or key-on return change is authorized by this unit.
