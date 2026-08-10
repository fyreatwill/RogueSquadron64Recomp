# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s585 recap (read this first)

| Observation | Implication |
|-------------|-------------|
| 0 RDRAM writes for 7913 ms / 237 E9 re-submits | dual FULL_SYNC is **sticky**, not re-emitted/task |
| 1 write E9→E7 at task~#5569 | stop = **one overwrite**, not path death |
| dual DL trees identical across edge | H6a REFUTED |
| dpc_bridge drops size-8 PIPE_SYNC (op 0x27) | sticky E7 → runner syncs=0 |
| force recovers @ 0x76A838 after 688 zeros | not permanent on force path |
| natural s577 open 772-zero tail | H6c SUPPORTED (no instruments for slot) |

Artifact: `scratch/s73_post_a_scene/s585_hsync4_offline/ANALYSIS.md`.

## This iteration's work unit

**Who writes E9→E7 into phys 0x76DF60 at the dual edge — RSP LLE single-cmd
scratch, or a guest store?**

Prefer the highest-information cheap path first:

### Hypotheses
- H7a: Factor5 LLE writes every RDP command through a fixed 8-byte RDRAM
  scratch at 0x76DF60; terminal FULL_SYNC is sticky only because the last
  command of each task re-points DPC at leftover E9 until a later task's
  PIPE_SYNC (normal mid-stream op) overwrites the scratch.
- H7b: Guest CPU writes the E9→E7 (or the whole terminal command) outside
  the RSP task.
- H7c: Sticky re-submit is a **bridge artifact** — `rs64_dpc_reset` + leftover
  DPC regs re-forward RDRAM the current task never issued; overwrite is
  incidental.
- H7d: Natural dual phase never uses sticky 0x76DF60 (force-path only).

### Discriminating measurement
1. **Instrument (one build):** on `[fs-slot] event=write` when cur becomes
   E7/E9 clean form, log **RSP IMEM PC** (if inside LLE task) and/or
   **last-guest-pc** / host return if guest. Same-run positive control: the
   known E7→E9 at dual entry and E9→E7 at stop must both log.
2. Optional same build: count per-task size-8 submits at ALL addrs (not just
   slot) to see if 0x76DF60 is unique terminal scratch.
3. If instrument is heavy: enqueue natural force-free soak with existing
   `LOG_FS_SLOT` only to settle H7d first (no new code).

### Exact commands (if instrument lands)
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# rebuild after instrument, then force-exit dual (known E9→E7):
env PROBE_MODE=start_only HOLD_S=45 ROGUESQ_FORCE_CASE5_START=40 \
  ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
  GAME_EXTRA_ENV="ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_FS_SLOT=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s586_hsync4_writer 5 12
```

### Outcomes
- write fires only under RSP task with IMEM PC in emit path → H7a
- write fires with guest PC / outside task → H7b
- slot submits without matching mtc0 DPC_END this task → H7c
- natural dual never arms sticky E9 @76DF60 → H7d

### Do NOT
- Wire product FULL_SYNC inject before knowing the writer.
- Re-litigate H6a/H6b/H6d.
- Chase leave-path crashes.
