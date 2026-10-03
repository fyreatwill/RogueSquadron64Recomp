# Next work unit: identify the upstream source of the zero DMEM payload

HYPOTHESIS-ID: m5-upstream-zero-dmem-producer

s3802 selected the immediate port-side RSP/vector/DMA chain. Both port arms
reached title and hangar with positive controls. The image arm repeatedly read
all-zero `0x1798B0..0x179A48` from DMEM `0xCB0`; source-transition and DMEM
coverage rows independently show zero-valued vector/DMA production before the
RDRAM write, and no guest CPU store overlaps the source span. Retail controls
were live, but retail hangar payload parity was not reached before the bounded
run stopped.

Competing hypotheses and discriminator:

- H1: the zero DMEM payload comes from a legitimate upstream RSP source DMA or
  task-data fill; a complete source-DMA/DMEM census joins its descriptor and
  value to the later `0xCB0` input DMA.
- H2: the observed vector/DMA chain is only a downstream clear/copy; the
  upstream source descriptor is absent, stale, or unrelated to the image task.
- H3: the port is using the wrong source descriptor/range; a same-run retail
  hangar watch disagrees with the port's source span or producer ordering.

The discriminating measurement is one batched, phase-gated census of every
source DMA into the task's DMEM input/output windows plus every DMEM writer
overlapping `0xCB0..0xE48`, joined by task generation and the later image input
DMA. The retail oracle must remain alive through hangar while watching the
same physical source span and producer PC `0x800078EC`. H1 predicts a complete
zero source-DMA join; H2 predicts an incomplete or unrelated upstream chain;
H3 predicts retail/source-span or producer-order disagreement. Whole-RDRAM and
both target-VI controls must fire in the same run.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_m5_source_input_writer.sh

Do not add a mitigation or alter the SP-yield/audio contract. If the census
is incomplete or the retail arm misses title/hangar, classify the run invalid
and repair coverage before drawing a writer conclusion.
