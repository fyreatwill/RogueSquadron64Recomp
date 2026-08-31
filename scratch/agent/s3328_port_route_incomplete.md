# Session 3328 — port image arm at VI-1024: vi-commit absent, slot-pool leaks

## Setup

Script: `scratch/agent/run_s3327_m5_slot_status_port.sh`
Flags: `ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1
ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_B40_WRITER=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1
ROGUESQ_LOG_FILTER_VOICE_AUDIT=1`
Autopilot: `3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a`
`ROGUESQ_AUTOPILOT_STOP_WIDTH=512`
`PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1`
Watchdog: 180 s SIGKILL.

## Phase transitions

- VI-0 at 1.4 s
- VI-320 at 1.4 s
- VI-640 at 3.2 s
- VI-1024 at 14.6 s
- VI-512: never reached. SIGKILL at 180 s.

## Controls passed

- 31,512 `audtask-join` rows (audio task lifecycle complete, image arm active)
- 89 `pcm-boundary-source` rows, 89 `pcm-boundary-consumer` rows (PCM contract live)
- 6,308 `audtask-dma-row` rows (DMA stages executing)
- 7,796 `m5-route-prepare accepted=1` rows in phase 4 (route prepared for each task)

## Key finding 1: vi-commit for VI-1024 absent

Total vi-commit events in the run: 10 (seq=0..9).
Last vi-commit: `seq=9 caller=0x80007904 mode_ptr=0x80128DA0 requested_width=1024
committed_width=640 committed_origin=0x696100 phase=3`.
This shows the port called the VI-mode set path with width=1024 while in phase 3
(VI-640), but the M5 route's committed state was still 640. No subsequent vi-commit
with committed_width=1024 appeared. All 7,796 phase-4 route-prepare rows show
`commit_seq=9 commit_width=640 commit_phase=3 key_match=0`.

## Key finding 2: slot-pool count grows monotonically

- t=6.6 s: 4 slots
- t=9.9 s: 473 slots
- t=10.9 s: 668 slots
- t=64.5 s: 1,578 slots

Count is strictly non-decreasing. No slot-freeing log row observed. This is a
new observation not recorded in s3325/s3326.

## Negative results

- No `B40-writer`, `slot-allocation`, `slot-submission` rows.
- Autopilot fired all 8 events (confirmed in log). Game did not respond by
  advancing to VI-512.
- No crash or abort marker in log.

## Hypothesis selection

- `H-PortRouteStillIncomplete` SELECTED: port image arm cannot reach hangar 512
  within 180 s.
- `H-PortMatchesRetail` NOT SELECTED: no hangar qualification.

Candidates for the VI-1024 stall:
- `H-VICommitAbsent`: no vi-commit for 1024 → M5 route key stale for all phase-4
  tasks (key_match=0).
- `H-SlotPoolExhausted`: slot-pool grows to 1578 unreleased → possible stall in
  a slot-wait path.
These must be discriminated in the next iteration (see NEXT.md).

## Log location

`scratch/agent/s3327_m5_slot_status_port/image.log` (556,576 lines, 180 s run)
