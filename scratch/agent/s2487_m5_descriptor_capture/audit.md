# s2487 — gspTask descriptor capture at osSpTaskYielded boundary

Date: 2026-08-26

## Recipe failures diagnosed (s2486 and prior)

Two orthogonal bugs blocked all previous descriptor captures:

**Bug 1 — missing audio route gate-opener.** `rs64_audio_current_route_snapshot`
reads `g_current_audio_route.active`, which is set from `rs64_audio_route_set`,
which is only called when `audio_route_log_enabled()` returns true. That check
requires one of `ROGUESQ_LOG_ALL`, `ROGUESQ_LOG_AUDIO_RETURN`, or
`ROGUESQ_LOG_M5_TASK_CONTRACT`. None were in the s2486/s2487 NEXT.md command.
Without the gate-opener, every phase-gated hook (descriptor-yield,
descriptor-start, scheduler-id) returns immediately regardless of VI width.
This explains zero descriptor rows in s2486 even when the game reached the
target phase in run 1 (48.4 s after boot).

**Bug 2 — incorrect phase-gate recipe.** The s2487 NEXT.md used
`PROBE_PHASE_WIDTH=1024` with `PROBE_KEYS_FROM_PHASE=1`. Keys fire only AFTER
1024 is reached; they cannot help reach 1024. The game at 640 (attract) must
advance to 1024 (title) on its own, which takes variable time and fails within
180 s on most attempts. Boot-relative keys at 15 s, 30 s, 45 s reliably advance
the game to 512 (hangar) by 48–49 s.

## Corrected probe

`ROGUESQ_LOG_AUDIO_RETURN=1` added (lighter than TASK_CONTRACT — avoids the 4 KB
DMEM snapshot). `PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=300` with boot-relative
`PROBE_KEYS='15:start 30:start 45:start ...'` (no PROBE_KEYS_FROM_PHASE).

Run: `scratch/agent/s2487_m5_descriptor_capture_d/run.log`

## Controls

- Resolver positive control: `[m5-dispatch-boundary-control]` fired at early boot
  (width=320). No target-phase dispatch control (the resolver call is in a
  different game phase from the hangar).
- Image-stage rows in prior `_c` capture confirmed Factor 5 image arm active at
  width=1024.
- `m5-scheduler-id-control` fired at width=1024 (title) and width=512 (hangar),
  confirming the audio route snapshot was live in both target phases.

## Descriptor capture results

1602 `m5-descriptor-yield` rows total; 74 in the hangar (512/0x6AB400) phase.
The sixteen words at gspTask (0x800377C8) are IDENTICAL and STABLE across every
observation in both phases:

```
words=0A8C2907,88C3045E,20848201,2907F858,17F04A94,911C317E,1FE145F4,12060623,
      1FE16082,C12A50A7,84820188,07F85820,5F8A9C29,4470CB04,7F8317E0,4818188C
```

These sixteen words are captured via the same endian-broken struct cast noted in
s2484 (using raw pointer offset with `^3` correction for the FIRST byte only, not
per-field). The values cannot be directly mapped to OSTask field names without a
MEM_W-based per-field decoder.

## Scheduler dispatch rows (width=512)

In the hangar phase:
```
event_ptr=0x80112AE0 or 0x80128CE0, event_payload=0x800377C8, task_ptr=0x800377C8
```

`event_payload = task_ptr = gspTask = 0x800377C8` — consistent with s2484.
`yield_match=1, payload_match=1` in descriptor-start rows (task started IS gspTask,
matches both yield and event-payload slots).

## Phase distinction

In the **title** (1024) phase: event_payload=0x800377C8 but the task started is
0x80149470 (distinct). In the **hangar** (512) phase: the task started IS
0x800377C8 (gspTask). The s2484 "H-LaterTaskHandoff" finding (distinct started task)
applies only to the title phase; in the hangar, gspTask is both payload AND started
task — a yield-and-restart cycle.

## Verdict

- **H-DescriptorPopulated SELECTED**: 74 yield rows in hangar phase with non-zero,
  stable sixteen-word fingerprint. The descriptor is populated at the yield boundary.
- **H-DescriptorStaleOrEmpty REFUTED**: descriptor is non-zero and consistent.
- **H-DescriptorWriterUnjoined REFUTED** at dispatcher boundary: `event_payload ==
  gspTask == started task` in the hangar phase; the writer chain closes at the
  scheduler dispatch.

Open: the sixteen words are endian-invalid (struct cast bug). The next step is a
MEM_W-based per-field decoder to read correct field values (type, data_ptr,
yield_data_ptr, etc.) and compare to retail ground truth.
