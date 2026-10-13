# Next work unit

HYPOTHESIS-ID: ovl2c-real-splice

Work unit: land the real overlay-0x2C RSPRecomp splice and validate it once.
This remains blocked on a human permission change; do not retry the denied
RSPRecomp command until the allow rule is added.

Required human action: add both Bash allow rules named in
`scratch/agent/UNBLOCK.md` for `../N64Recomp/build/RSPRecomp` and its absolute
path variant.

Once unblocked, from the repo root run
`../N64Recomp/build/RSPRecomp factor5_rsp_ovl2c.toml`, wire the existing
`scratch/agent/fixup6r_draft.py` into `tools/fixup_factor5_ucode.py`, run the
normal `make_elf.py -> N64Recomp -> fixup_game_funcs.py` regeneration chain,
then run `cmake --build build --config Debug --target RogueSquadron64Recomp`.
Use the s4753 direct mission driver with
`ROGUESQ_OVL2C_DROP=0`. Capture positive controls for VI 512 at
`0x00690400`, no crash/abort, and per-task runaway count.

Competing hypotheses and discriminator:

- H1: the real 0x2C image emits the missing billboard/sprite content while
  keeping the DL bounded.
- H2: the splice has an ABI/table/extern mismatch and crashes or re-enters the
  restart loop.
- H3: the covered mission defects are unrelated to 0x2C.

DISCRIMINATING MEASUREMENT: one rebuilt binary and one phase-gated mission
capture. H1 predicts bounded 0x2C activity plus changed sprite content; H2
predicts a crash or runaway recurrence; H3 predicts the s4753 bounded route
and unchanged mission content. The experiment that refutes this block is an
allowlisted RSPRecomp invocation that emits C for `factor5_rsp_ovl2c.toml`.
