# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

OPEN DEPENDENCY (human, NOT to be retried by iterations): RSPRecomp is not in the headless
allowlist (denied s4741-s4745). Do NOT run it. The 0x2C splice (fixup 6r draft at
scratch/agent/fixup6r_draft.py, toml factor5_rsp_ovl2c.toml) resumes only when a human adds
the allow rules (see scratch/agent/UNBLOCK.md) and removes this paragraph.

s4748 result: first 0x2C dispatch = op 0xBD (3/3 runaway ring snapshots, prevop=0xBD at d153 0x28->0x2C).

Work unit: add per-task counters in src/rsp/dpc_bridge.cpp dlwalk fetch loop: count of 0xBD ops and
count of 0xBD ops that reach 0x1DB0 with d153==0x2C, for every task; run s4746_run.sh once.
Hypotheses: H-bd-always-2c (every 0xBD reaches 0x2C; runaway tasks are simply those whose DL has
0xBD); H-bd-conditional (some 0xBD ops handled resident, only a sub-variant picks 0x2C);
H-bd-in-normal-too (normal tasks contain 0xBD yet never reach 0x2C -> selector is not the op alone).
Discriminator: table of (#0xBD ops, #2C arrivals) per task, normal vs runaway. Positive control: the
existing n2c counter (142/142 runaway). Negative: phase-4 title tasks.
