# NEXT work unit (s2488) — fix endian decode in descriptor yield logging

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Context

s2487 captured the sixteen gspTask words at the `osSpTaskYielded` boundary in
both the title (1024) and hangar (512) phases. The words are non-zero and stable:
`0A8C2907,88C3045E,20848201,2907F858,17F04A94,911C317E,1FE145F4,12060623,
1FE16082,C12A50A7,84820188,07F85820,5F8A9C29,4470CB04,7F8317E0,4818188C`.

These values are endian-invalid. The descriptor-yield hook uses a raw struct cast
starting at `(task_ptr - 0x80000000) ^ 3`, which misaligns every field boundary.
The correct approach is MEM_W per field (the same macro used throughout the
recompiler generated code for 32-bit reads from RDRAM).

## Single work unit

Fix `rs64_m5_descriptor_yield` in `src/main/main.cpp` to read each of the sixteen
OSTask words via `MEM_W(task_ptr, offset * 4)` instead of struct cast. Re-run the
corrected probe and compare the decoded field values (especially `type`, `data_ptr`,
`data_size`, `yield_data_ptr`, `output_buff`) to expected N64 task values and to
retail ground truth if available.

## Competing hypotheses

- H-DescriptorLegitimate: the decoded fields show valid N64 task values (type=2
  for M_AUDTASK, data_ptr in RDRAM range 0x80xxxxxx, yield_data_ptr correct).
  This would confirm gspTask carries a valid audio task descriptor in the hangar.
- H-DescriptorGarbage: the decoded fields show implausible values even after
  endian correction — type not 1 or 2, pointers out of RDRAM range, etc. This
  would suggest gspTask is stale or holds an unexpected task type.

## Discriminator

A single corrected probe must emit `[m5-descriptor-yield]` rows with
`decoded_type`, `decoded_data_ptr`, `decoded_yield_data_ptr`, etc. that are either
in valid N64 address/value ranges (selects H-DescriptorLegitimate) or not (selects
H-DescriptorGarbage). The scheduler-id row `task_ptr=0x800377C8` at 512/0x6AB400
must fire as positive control.

## Fix location

`src/main/main.cpp`, function `rs64_m5_descriptor_yield` (around line 1502).
Replace the struct cast words array with:
```cpp
const uint32_t words[16] = {
    MEM_W(0, task_ptr + 0x00), MEM_W(0, task_ptr + 0x04),
    MEM_W(0, task_ptr + 0x08), MEM_W(0, task_ptr + 0x0C),
    MEM_W(0, task_ptr + 0x10), MEM_W(0, task_ptr + 0x14),
    MEM_W(0, task_ptr + 0x18), MEM_W(0, task_ptr + 0x1C),
    MEM_W(0, task_ptr + 0x20), MEM_W(0, task_ptr + 0x24),
    MEM_W(0, task_ptr + 0x28), MEM_W(0, task_ptr + 0x2C),
    MEM_W(0, task_ptr + 0x30), MEM_W(0, task_ptr + 0x34),
    MEM_W(0, task_ptr + 0x38), MEM_W(0, task_ptr + 0x3C),
};
```
(Verify the MEM_W macro signature in the include context — it may need `rdram` as
first argument.)

## Corrected probe command

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_DESCRIPTOR=1 ROGUESQ_LOG_M5_SCHEDULER_ID=1 ROGUESQ_LOG_M5_SECOND_EXEC=1 ROGUESQ_LOG_AUDIO_RETURN=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=300 PROBE_KEYS='15:start 30:start 45:start 60:start 75:start 90:start 100:start 110:start 120:start 130:start 140:start 150:start 165:start 180:start' PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s2488_m5_descriptor_decode 120 1`

Do NOT use PROBE_KEYS_FROM_PHASE. Do NOT use ROGUESQ_LOG_M5_TASK_CONTRACT
(causes early Metal framebuffer crashes before reaching the hangar).
