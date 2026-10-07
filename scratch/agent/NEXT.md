# Next work unit: M5 Step 4d immediate consumer of the qualified 94648 span

HYPOTHESIS-ID: m5-audio-step4d-94648-consumer

Session 4077 qualified the port `0x80094648` indexed store. The next single
experiment is to identify whether the written `0x80141AD8..` channel span is
read/copied into the image/PCM path, or whether the port diverges immediately
after the store.

Competing hypotheses:

- Hconsumer-live: a retail-shaped post-store read/copy occurs in the hangar
  phase and reaches the downstream image/PCM input; the zero payload is later.
- Hconsumer-absent: retail has a post-store read/copy but the port has no
  matching phase-scoped consumer activity after the qualified store.
- Hconsumer-value: both arms consume the span, but the port's read/copy value
  or destination differs from retail.
- Hcoverage: either arm lacks the whole-RDRAM/title/hangar controls or the
  qualified `m5-94648` positive control, making a null unevaluable.

Discriminating measurement: first use the retail oracle to ground-truth reads
of physical `0x141AD8..0x141AF0` after the `0x80094648` stores, including PC and
destination attribution. Then batch one port witness for the selected retail
consumer idiom and run one same-build isolated image capture with
`PROBE_PHASE_WIDTH=1024` and `PROBE_KEYS_FROM_PHASE=1`. Require the retail
whole-RDRAM/title/hangar controls, port title/hangar gates, and
`m5-94648-control`/hangar rows. Hconsumer-live selects matching post-store
read/copy rows and downstream nonzero handoff; Hconsumer-absent selects valid
controls plus retail rows but zero port rows; Hconsumer-value selects paired
rows with a value/destination mismatch; Hcoverage selects any missing control.

Exact preparation/run: inspect the retail consumer with bounded `rg`/oracle
watch output before adding a witness; then regenerate with
`python3 /Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py`,
`/Users/williambuckley/Documents/Tools/N64Recomp/build/N64Recomp rogue_squadron.toml`,
`python3 fixup_game_funcs.py`, build with
`cmake --build build --config Debug --target RogueSquadron64Recomp`, and run
`zsh scratch/agent/run_s4075_m5_step4_94648.sh`. Keep all output under a new
`scratch/agent/s4078_m5_step4d_94648_consumer` directory; SIGKILL both arms.
Do not change the gate or add a mitigation from a port-only zero.
