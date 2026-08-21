# NEXT work unit (s2118) — retry M5 C88=0 image-task contract A/B

HYPOTHESIS-ID: m5-image-task-contract

## Work unit

Run one fresh same-build, phase-keyed C88=0 stub/image A/B with the existing
`run_mission_keys.sh` LLE-forced/spin-yield route. The s2117 stub reached title
and hangar, but the image arm crashed in the pre-target 640-wide phase before
any contract row. Use C88=0 for both arms so the contract rows share one route
recipe. Do not change task fields, DMA, exit mapping, output routing, canary,
slots, PCM, waits, guards, queues, or default behavior.

## Competing hypotheses and single discriminator

- H-TaskExitMapping: the image arm's generated DMEM/DMA activity and stage/PCM
  joins are legitimate, and its final `break 0` is correctly represented by
  host `Broke`; `output_buff=0` is not by itself a failed output route.
- H-OutputRoute: the image task reaches the host but `output_buff=0` means the
  task is routed to the wrong destination, so the image-side stage rows do not
  join the expected PCM source/consumer rows.
- H-WritebackLoss: image-side stage evidence exists, but generated DMA does
  not produce the matching RDRAM span observed by the consumer.
- H-NoValidOutput: the image arm reaches its task exit but produces only zero
  or invalid destination payloads at the target phase.

The single discriminator is one phase-keyed stub/image table at title and
hangar containing `audtask-abi` fields (`output_buff`, `output_buff_size`,
`exit`, `break_pc`, `canary_ok`), generated DMA count/ranges, image stage rows,
PCM source/consumer address/length/hash/nonzero joins, completion ordering,
wait/queue edges, and the stub control rows. A matching nonzero stage-to-PCM
join with completion before the consumer, `break_pc=0x1328`, and the observed
image canary edge selects H-TaskExitMapping. A stage row without the expected
consumer selects H-OutputRoute; a stage/DMA mismatch selects H-WritebackLoss;
only zero or invalid target destinations selects H-NoValidOutput. Empty rows
are coverage failures, not contract results.

## Exact commands

Use the existing Debug binary and launch both arms concurrently from the
repository root:

    env GAME_EXTRA_ENV='ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_WAIT_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2118_m5_contract_stub_c0 30 12 > scratch/agent/s2118_m5_contract_stub_c0_driver.log 2>&1
    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_WAIT_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2118_m5_contract_image_c0 30 12 > scratch/agent/s2118_m5_contract_image_c0_driver.log 2>&1

Inspect only phase lines, positive-control counts, target contract rows,
join/order fields, crash tails, and the driver summaries. If either arm
misses a target phase, record the table as a coverage failure and do not
interpret empty contract fields.
