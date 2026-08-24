# NEXT work unit (s2224) — compare port key-on transfer state by phase

HYPOTHESIS-ID: m5-audio-keyon-contract

## Work unit

Extend the existing s2122 key-on census in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` with a
diagnostic-only table for the eight post-guard transfer PCs
`0x80090CF0`, `0x80090D08`, `0x80090D34`, `0x80090D4C`, `0x80090D78`,
`0x80090D90`, `0x80090DBC`, and `0x80090DD4`. Record the same
`$v0/$s1/$a0/$a2` tuple as the retail oracle, plus per-site divide and guard
counts, keyed to 640 origins `0x00696100`/`0x00696600` and hangar
`512 @ 0x006AB400`. Keep every existing key-on divide guard and early return
unchanged. Build once, run one qualified image-arm capture, and compare the
port table with s2223's retail matrix.

Competing hypotheses and the single discriminator:

- H-PortRetailLike: all eight transfer PCs execute in the covered port phase
  buckets, divide and guard counts remain zero, and the port tuple sets follow
  the retail phase split. The existing early-return class is not the cause.
- H-PortGuardSuppression: one or more port guard rows are positive and the
  corresponding transfer PC is absent in a bucket. The current guard/return
  machinery suppresses a retail alternate path.
- H-PortTupleStateMismatch: transfer rows are present with zero guards and
  divides, but the port tuple sets do not match retail's phase-specific state.
  The next work is the branch-tested voice/slot state, not guard removal.
- H-PortCoverageFailure: positive normal-tail, slot, and phase controls fire,
  but target/hangar transfer rows are absent. No branch conclusion is allowed.

The discriminator is one phase-keyed matrix with eight transfer counts, eight
divide counts, eight guard counts, and bounded `$v0/$s1/$a0/$a2` tuple sets for
each of the three buckets. Positive controls must include the existing audio
dispatch/normal-tail/slot rows and both target plus hangar VI phases. A guard
hit selects H-PortGuardSuppression; zero guards/divides with retail-like
tuples selects H-PortRetailLike; zero guards/divides with changed tuples
selects H-PortTupleStateMismatch; missing controls selects
H-PortCoverageFailure.

## Exact commands

1. Add the transfer-site table to the existing regeneration-safe s2122 block,
   then regenerate in the required order:

~~~sh
cd /Users/williambuckley/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
zsh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/agent/regen_n64recomp.sh
python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py
cmake --build /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build --config Debug --target RogueSquadron64Recomp
~~~

2. Run the one qualified port capture from the repository root:

~~~sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2224_port_keyon_transfer 30 12 > scratch/agent/s2224_port_keyon_transfer_driver.log 2>&1
~~~

Use the port log's positive controls first, then an awk matrix over the three
phase keys. Do not infer a branch or authorize a return change from counts
without the transfer tuple sets.
