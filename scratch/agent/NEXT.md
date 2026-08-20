# NEXT work unit (s1978) — is 0x801714D0 a voice table or leftover text?

HYPOTHESIS-ID: hangar-frame-freeze

## What s1977 settled

Drain call=1 leftover slots are a frozen 13-zombie set: `ch=18
base=0x801714D0 dest_ok=1 nz=13` for 10M iters. Bytes `. o \n sBgm c a
\xFF` at 0x88 stride; idx 10,11,13,15,17 are 0; none is `0x02`. H-one-zombie
/ H-chCount-wild / H-tick-rekeys REFUTED. Force-idle still does not restore
`fs`. Positive control: `[drain-tick] call=1 iters=1 gate=0x01`.

## Competing hypotheses (what lives at the table)

- **H-ascii-heap:** `0x801714D0` is not a live voice array. Consecutive
  bytes are a C string / text dump; 0x88-stride just samples printable
  chars. `isAudioSlotActive` treats them as status.
- **H-voice-records:** the 0x88 records are real MusyX channel structs
  (KSEG0 pointers, typed fields). byte+0 just is not `0x02` on this path.
- **H-count-desync:** s1943 retargeted this address with count=15; ch=18
  walks 3 slots past the allocation. idx16=0xFF is the past-end sentinel.
- **H-never-keyed:** records are the live table, but byte+0 was never
  written as key-on `0x02` and never cleared (stale heap / skipped init).

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep the s1977 `[drain-slots]` idx+byte dump. On the same `[drain-tick]`
samples (first 8 + every 100k), also log:

1. 32 consecutive bytes at `base` as hex + ASCII (`[drain-base]`).
2. First 16 bytes of slot 0 (`base+0`) and slot 16 (`base+16*0x88`)
   (`[drain-hdr] idx=0|16`).
3. Enable existing `slot-alloc` via `ROGUESQ_LOG_VI_CALLERS=1` (no new
   counter) so the live `allocateSongChannelArray` `new`/`count` is in
   the same run.

Outcomes:
- consecutive 32 at base is a C string → H-ascii-heap
- 0x88 records show KSEG0 pointers / typed fields, byte+0 is a status
  nibble → H-voice-records
- slot-alloc count=15 at `0x801714D0` while ch=18, and slot-16 header
  is not a record → H-count-desync
- records look real, slot-sb never writes `0x02` at this base → H-never-keyed

Positive control: `[drain-tick] call=1 iters=1 gate=0x01` still fires,
plus at least one `[avf-gate] site=slot-alloc` before drain (the boot
`0x8018D4A0 count=16` alloc). Keep `ROGUESQ_SPIN_YIELD=1`. Leave the 10M
timeout in place.

## Exact patch site

`apply_s1976_drain_tick` in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
and the matching `[drain-slots]` block in `RecompiledFuncs/funcs_30.c`
(SENTINEL is already applied — incremental edit, do not rerun full fixup).

Log tags: `[drain-base]`, `[drain-hdr]`.

## Exact test

```sh
mkdir -p scratch/agent/s1978_drain_base
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1978_drain_base 60 2
```

60s after hangar is enough: s1977 hit 10M / timeout well before that.
