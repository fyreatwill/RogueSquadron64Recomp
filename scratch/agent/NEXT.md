# Next work unit: qualify the Step 7 status-03 worker contract on silent audio

HYPOTHESIS-ID: m5-step7-status03-silent

Competing hypotheses and discriminator:

- H-chain-live: the located generated tree/fixup produces the named worker
  entry, `0x8009B7EC` zeroing store, and return on the silent arm.
- H-chain-absent: the silent arm reaches both phase gates but none of the
  status-03 entry/store/return edges occurs.
- H-route-invalid: the silent arm does not reach both target phases, so a
  status-03 null is unevaluable and the next discriminator is startup route
  topology rather than worker behavior.

The single discriminating measurement is one same-build retail-gated silent
capture, phase-gated on title `0x00790400:1024` and hangar `0x006AB400:512`,
with the existing status-03 entry/store/return probes enabled. Positive
control must fire and both retail phases must pass. A complete entry -> store
-> return chain selects H-chain-live; paired phase-qualified absence selects
H-chain-absent; missing silent phase gates selects H-route-invalid. Do not
alter the wait or force-clear status.

Exact commands:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Then run the new single-arm recipe from the repo root:
`zsh scratch/agent/run_s4117_m5_status03_silent.sh`

The recipe must launch the retail oracle first, wait for its whole-RDRAM
positive control, launch only `ROGUESQ_AUDIO_UCODE=0`, SIGKILL its process,
and write a verdict plus bounded status-03 rows under
`scratch/agent/s4117_m5_status03_silent/`.
