# Classify the source records used by rs_strncpy caller 0x80022B44
HYPOTHESIS-ID: m5-audio-destub

s4602 selected caller `0x80022B44` in the qualified VI-640 phase. It copies
five 16-byte chunks from `0x8062B9F8`, `0x8062BA1C`, `0x8062BA40`,
`0x8062BA64`, and `0x8062BA88` to `0x801724C0..0x80172510`; the fourth
source supplies `late` at destination offset `0x34..0x37`. Retail independently
writes the same physical span from `0x80007670`, but its source identity is
still unknown.

Competing hypotheses:

- H-name-table: `0x8062BA64` is a legitimate name-table/string record and
  caller `0x80022B44` is the normal retail-shaped table copy.
- H-port-corrupt-source: the source bytes at `0x8062BA64` are malformed or
  port-only; the caller is legitimate but its source publication diverges.
- H-generic-record-copy: the caller copies a generic 16-byte record, so
  `late` is incidental data and the audio crash boundary is unrelated to its
  semantic name use.

Discriminating measurement: one build and one phase-gated run. Extend the
existing regeneration-preserved `s4602` caller hook only for caller
`0x80022B44` to dump the 16 source bytes at each selected `a1` and the
destination, with a same-run control from another caller and the existing
entry/adjacent/span controls. Printable name bytes and a stable source-table
address select H-name-table; non-name or changing source bytes select
H-port-corrupt-source; a record-shaped non-name payload with unchanged copy
semantics selects H-generic-record-copy. Do not add a mitigation.

Before building, add the source-byte dump to
`tools/apply_s4602_strncpy_callers.py` and its host helper, then run:

```sh
python3 tools/apply_s4602_strncpy_callers.py
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run from `build/` on this macOS single-config tree with the same qualified
environment as s4602, adding `ROGUESQ_LOG_S4602=1`, and capture under
`scratch/agent/s4603_source_records/`. Use a SIGKILL watchdog and retain
`PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1`.
