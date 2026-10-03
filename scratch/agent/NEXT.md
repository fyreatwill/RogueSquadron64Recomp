# Next work unit: identify the legitimate writer of the zero source span

HYPOTHESIS-ID: m5-source-input-writer

s3801 selected the source-input boundary. The same-build image/silent arms both
reached title and hangar with positive phase, PCM, audio-return, and stability
controls. Image-stage source DMA, stage DMEM/DMA, and destination payloads were
zero while the image consumer callback was live; silent had no image-stage rows
but retained PCM controls. Independent retail control reached title/hangar.

Competing hypotheses and discriminator:

- H1: the legitimate source-span writer/fill runs before the image input DMA
  and writes zero; a phase-gated writer census names it and joins its value to
  the zero DMA generation.
- H2: a non-writer path or stale object supplies the zero source span; the
  complete writer census has no matching zero writer, or its range/object does
  not join the DMA source.
- H3: the port source reader is observing the wrong physical range; the
  independent retail watch and same-run descriptor/source controls disagree on
  the span or producer PC.

The discriminating measurement is one batched, phase-gated producer census for
every CPU/RSP write class overlapping `0x1797B0..0x179A48`, joined by task
generation and source-DMA event, with the retail oracle watching the same span
and producer PC `0x800078EC`. H1 predicts a legitimate zero writer joined
before each image input DMA; H2 predicts no complete writer join; H3 predicts
retail/source-span or producer-PC disagreement. Whole-RDRAM and both target-VI
controls must fire in the same run.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_m5_source_input_writer.sh

Do not add a mitigation or alter the SP-yield/audio contract. If the census
is incomplete or the retail arm misses title/hangar, classify the run invalid
and repair coverage before drawing a writer conclusion.
