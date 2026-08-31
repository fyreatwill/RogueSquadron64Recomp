# NEXT work unit — M5 Step 1 supervised route requalification

HYPOTHESIS-ID: m5-step1-image-silent-qualification

Run one supervised image-versus-silent pair after fixing the runner lifetime.
The prior s3324 capture was invalid because both port arms stopped at VI 640;
do not interpret its audio nulls.

## Competing hypotheses

- `H-AudioDegeneracy`: after both arms reach the target phase, only the image
  arm adds service, slot/voice, or PCM progress.
- `H-ContractGap`: the image reaches the target phase and completes DMEM/DMA
  work, but the guest output/PCM chain remains open.
- `H-RouteOnly`: both arms have matching downstream rows; any difference is
  route/timing rather than an audio-owned contract edge.

## Discriminator

Use one build and concurrent arms with the existing complete probe set. The
same capture must show whole-RDRAM oracle control, port VI 1024 and 512 phase
controls, then dispatch → task fields/source → DMEM/DMA → image exit/SP →
service → status/slot/voice → PCM source/consumer. Image-only downstream
progress selects `H-AudioDegeneracy`; image completion without output joins
selects `H-ContractGap`; matching rows select `H-RouteOnly`. Otherwise the
run is invalid and selects nothing.

## Exact command

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s2286_m5_step1_trace_light_pair.sh s3325_m5_step1
```

If the foreground supervisor cannot remain attached, run the same command
under a process supervisor that preserves the full process group until its
driver log reports the pair summary; do not use a stopwatch-only run.
