# Next work unit: execute the next bounded M5 de-stubbing edge

HYPOTHESIS-ID: m5-audio-destub-step2

Do not rerun the source-producer census until a new route discriminator exists.
Session 4131 had no qualified port target phase: one real-audio arm crashed in
640 and the corrected Start schedule stayed in 640. Execute one named,
regeneration-safe M5 audio contract edge from `docs/M5-AUDIO-PLAN.md`, keeping
the silent `ROGUESQ_AUDIO_UCODE=0` arm as the same-build control. Do not change
the guest source writer, image writeback, wait cap, slot predicate, or add a
mitigation.

Competing hypotheses and discriminator:

- H-audio-degeneracy: one real contract edge produces a new downstream task,
  service, slot, voice, or PCM control without merely changing route reachability.
- H-contract-gap: the edge changes task/DMEM/DMA or service identity, but the
  phase-scoped slot/PCM join remains closed.
- H-route-invalid: either arm lacks both target gates, so no audio-contract
  conclusion is allowed.

The single discriminating measurement is one same-build, phase-keyed table
covering dispatch/exit, task ABI, DMEM/DMA, service return, slot transitions,
PCM source/consumer joins, and title/hangar gates. A new downstream control
selects H-audio-degeneracy; task progress without downstream closure selects
H-contract-gap; either missing target gate selects H-route-invalid.

Commands:

1. Select the next single behavior edge from the incremental sequence in
   `docs/M5-AUDIO-PLAN.md`, and write its exact rollback/control arm here
   before building.
2. Build once:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run real and silent arms from `build/` with the qualified phase-gated
   route, the whole-RDRAM oracle positive control, and all task/DMEM/DMA/
   service/slot/PCM controls. SIGKILL at 120s.

Expected outcomes: both arms reach title/hangar and the changed edge selects
H-audio-degeneracy or H-contract-gap; a missing target gate leaves
H-route-invalid selected without interpreting null downstream counters.
