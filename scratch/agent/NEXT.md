# Next work unit: repair the paired M5 source-producer route

HYPOTHESIS-ID: m5-image-source-producer-context

Run one retail-gated source-producer context census, fixing the oracle watch
indexing and the port launch path before interpreting values. Do not change
the image, audio wait, cap, predicate, slot state, guest writer, or host
writeback.

Competing hypotheses and discriminator:

- H-port-writer-legitimate-zero: qualified retail and port reach hangar and
  agree on writer destination, value, loop/input context, and ordering.
- H-port-writer-context-split: both routes reach hangar, but the first
  phase-keyed argument, destination, loop-bound, value, or ordering split is
  at the port writer.
- H-route-invalid: either retail lacks title/hangar or the canonical port
  crashes before hangar; no writer conclusion is allowed.

The single discriminating measurement is a phase-keyed table containing the
retail `0x800078EC` PC/value/context rows, the port guest-store arguments,
source-span hashes, route ordinals, and both title/hangar gates. A matching
qualified table selects H-port-writer-legitimate-zero; a qualified context
split selects H-port-writer-context-split; either missing target gate selects
H-route-invalid.

Commands:

1. Run the oracle from the repo root with whole-RDRAM positive control,
   source-span watch, `--watch-pc 0x800078EC`, VI trace, and the validated
   repeated Start presses. Allocate memory-watch indices first, then use the
   actual printed index for `--post-value-watch`; do not assume the PC watch
   is index 1. Capture to `scratch/agent/soak_results/iter4131/retail.log`
   and use a background PID watchdog that SIGKILLs at 120s.
2. Build once:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run from `build/` as `./RogueSquadron64Recomp` with
   `ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1
   ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUTOPILOT=1`,
   `PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1`, and the existing
   source-producer, source-writer, source-transition, task-contract,
   audio-return, and PCM-boundary logs. SIGKILL at 120s or immediately after
   a qualified hangar capture.

Expected outcomes: retail and port both reach title/hangar and produce a
   comparable table (writer-legitimate-zero or context-split), or the port's
   pre-hangar crash reproduces and leaves H-route-invalid selected.
