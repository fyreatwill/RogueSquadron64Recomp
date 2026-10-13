# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

OPEN DEPENDENCY (human, NOT to be retried by iterations): RSPRecomp is not in the headless
allowlist (denied s4741-s4745). Do NOT run it. The 0x2C splice (fixup 6r draft at
scratch/agent/fixup6r_draft.py, toml factor5_rsp_ovl2c.toml) resumes only when a human adds
the allow rules (see scratch/agent/UNBLOCK.md) and removes this paragraph.

s4747 result: 0x2C arrival == runaway (142/142 vs 0/387). Phase-7 runaways have exactly one arrival.

Work unit: find what triggers the first 0x2C dispatch. Read the existing `[dlwalk-jmp]` ring lines
(scratch/agent/s4746_phase/run.log, `grep dlwalk-jmp`) for a phase-7 runaway vs a phase-4 normal
task: compare prev_op, r31, line, and the DL word that led to d153=0x2C.
Hypotheses: H-op-bd (a fixed 0xBD-prefixed command always selects 0x2C); H-data-dependent-index (same
opcode, but an index/arg in the DL, e.g. an object type absent in title/hangar, picks overlay 0x2C);
H-stale-d153 (d153 left over from an earlier task, not set by the current DL).
Discriminator: the DL word / DMEM operand preceding the first arrival; if the ring lacks it, add an
always-on capture of the 8-byte DL word at dispatch (one build, one run, s4746_run.sh).
Positive control: phase-3 runaways. Negative: phase-4 normal tasks show no arrival.
