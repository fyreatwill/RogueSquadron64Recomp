# Next work unit: join retail writer-PC arguments to task rows

HYPOTHESIS-ID: m5-task-output-contract-retail-parity

Session 3847 was capture-valid. The exact retail watch
`0x167000..0x169B00` had stable phase writers `0x80015BC8` and
`0x8000F3A0`; title counts were 86,146 and 117, hangar counts were 12,706
and 38,214. Retail had 627 title and 528 hangar type-2 task rows. The phase
histogram does not establish a per-task destination or length.

Before building anything, preserve these competing hypotheses and discriminator:

- H1: one writer PC receives the stage destination/length (or a directly
  joinable pointer) and its phase-gated rows repeat the port stage-2 role.
- H2: the writer PCs are unrelated bulk stores; their live arguments do not
  identify the task destination or length.
- H3: the oracle exposes neither enough writer arguments nor a stable join key,
  so exact task ownership is not measurable by this route.

Discriminating measurement: run one paired capture with the same whole-RDRAM,
title/hangar VI, type-2 task, and no-crash controls. Add `--watch-pc
0x80015BC8,0x8000F3A0`, phase-gated to `0x00790400:1024` and
`0x006AB400:512`, while retaining `--pc-hist-watch 1` and the exact target
watch. Compare the writer-PC GPR/argument rows against the task sequence and
port `audtask-image-stage-row` destination/length rows. H1 requires a stable
writer argument tuple matching the port stage-2 destination role; H2 requires
positive controls but no such tuple; H3 requires that the watched PCs cannot
yield a stable or interpretable argument tuple.

Starting command:

    zsh scratch/agent/run_s3848_m5_task_output_writer_args.sh

Create that self-contained paired recipe from
`scratch/agent/run_s3847_m5_task_output_contract_exact.sh`, changing only the
oracle options needed for the two writer-PC watches and bounded summaries.
Do not add a writeback guard or infer a destination from the port address.
