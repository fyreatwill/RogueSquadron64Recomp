# Session 5404 — M4 normalized boundary discriminator

## Work unit

This is an offline redesign of the parked M4 comparison. No runtime code or
mitigation is changed.

| ID | Prediction |
| --- | --- |
| H1 | After removing implementation-local task numbering and alternating framebuffer addresses, retail and port show the same transient VACC behavior at the same ucode instruction and task progress. |
| H2 | The normalized distributions still differ, identifying a real implementation divergence that warrants writer attribution. |
| H3 | One normalization key is not independently observable in both arms, so the comparison remains unevaluable. |

## Offline evidence and control

The existing oracle capture was re-run through
`tools/analyze_m4_task_join.py` before designing a new field:

```text
mid_records=3020766 graphics_tasks_with_mid=2083
end_graphics_tasks=2083 joined_tasks=2083 unmatched_mid=0
joined_with_8000=1222
vi_width_controls=4 whole_rdram_controls=2
end_tasks_with_8000=0 end_tasks_zero_8000=2083
```

This is a valid positive-control run, but it cannot provide an exact
cross-implementation task key. Retail task serials are local to the retail
run; the port target capture has one long graphics task (`task=959`). Raw
origins also alternate between `0x006AB400` and `0x006AB800`. Therefore
`(origin, task serial, PC, step)` is not a shared key. The prior exact join
correctly selected H3 without saying anything about the writer.

The PC mapping remains usable: port `0x112C` maps to retail IMEM PC `0x012C`,
and port `0x17F0` maps to `0x07F0`. It is not sufficient by itself because
port records are hook events while retail records are periodic samples, and
the arms partition graphics work into different task counts.

## Discriminating measurement

One batched instrument must emit a row at every selected mapped PC with this
portable key:

```text
(phase_epoch, ucode_overlay_id, mapped_imem_pc, progress_bucket)
```

`phase_epoch` is the ordinal of the 512-wide hangar VI phase, not the raw
framebuffer address. `ucode_overlay_id` is the loaded Factor 5 image or an
equivalent instruction-image hash. `progress_bucket` is the integer bucket
of `step / task_step_count` within that task. Each row retains:

```text
sample_count, lanes_equal_0x8000, first_8000_lane, last_8000_lane,
first_writer_pc, last_writer_pc, task_end_8000_lane_mask
```

The retail arm derives `task_step_count` from each task's observed step range.
The port arm exposes the same count at task end; it must not use a synthetic
stage ordinal. VI controls, a whole-RDRAM watch, and a live mapped-PC control
are required in the same run.

Decision rule:

- H1: at least 20 rows per mapped PC in both arms, with matching lane
  distributions within the same normalized keys and zero task-end masks.
- H2: at least 20 shared normalized rows per mapped PC exist, but a repeated
  lane or writer-PC mismatch remains in one key class. Only then is writer
  attribution authorized.
- H3: either arm lacks a live overlay ID, task-local step range, phase epoch,
  or mapped-PC positive control, or fewer than 20 shared rows can be formed.

This separates a real value/writer divergence from task partition and
framebuffer-address artifacts. It does not authorize a guard or skip; any H2
follow-up must identify the exact instruction that produced the value.
