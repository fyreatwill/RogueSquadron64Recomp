# NEXT work unit (s2276) — M5 key-on pointer-versus-branch discriminator

HYPOTHESIS-ID: m5-keyon-pointer-branch-discriminator

## Work unit

Use the existing regeneration-safe key-on census and one qualified port/retail
comparison to add the smallest pointer-versus-branch witness at all eight
post-guard transfer sites. Record the existing tuple
`(v0,s1,a0,a2)` together with the raw pointer operand/source word and the
branch selector/state word that chose the transfer path. Keep this diagnostic
only: do not change the key-on return, divide guards, slot stores, audio
default, or route gates. Use one build and one phase-gated run per arm, with
both arms prepared before running either.

## Competing hypotheses and discriminating measurement

- **H-PointerMismatch:** retail-only versus port-only tuple rows share the
  same branch selector/state but differ in the raw pointer operand or the
  pointed-to source word. This selects a pointer/data contract boundary.
- **H-BranchMismatch:** the pointer operand/source word agrees, but the
  branch selector/state differs at the transfer site. This selects a missing
  branch-state publisher or predicate boundary.
- **H-MixedPointerBranch:** both pointer/source and branch selector differ in
  the same common cells. The next unit must split the two inputs with a
  second phase-keyed capture; no key-on change is authorized.
- **H-CoverageInvalid:** either arm misses its title/hangar positive controls,
  the witness overflows, or the retail whole-RDRAM control does not fire. The
  tuple result is unevaluable and the route boundary remains the active
  blocker.

The discriminating table is one row per
`origin,width,transfer_pc,normalized_tuple` with columns
`port_or_retail,raw_pointer,source_word,branch_selector,branch_state,tuple_count,
overflow,phase_control,whole_rdram_control,title_gate,hangar_gate`. Equal
pointer/source with different branch fields selects H-BranchMismatch; equal
branch fields with different pointer/source selects H-PointerMismatch; both
different selects H-MixedPointerBranch; missing controls select
H-CoverageInvalid.

## Ground-truth prerequisite

Before editing the port census, run the retail oracle's whole-RDRAM positive
control and the existing key-on target watch in the same phase-gated recipe.
Only proceed if the whole-RDRAM watch fires at its expected high count and the
retail title/hangar gates are present; otherwise classify the arm as
H-CoverageInvalid. The port runtime is not ground truth for the new fields.

## Build

```sh
(cd ../rogue_squadron64 && python3 tools/make_elf.py)
(cd ../N64Recomp && ./build/N64Recomp rogue_squadron.toml)
python3 ../N64Recomp/fixup_game_funcs.py
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

```sh
zsh scratch/agent/run_s2276_m5_keyon_pointer_branch.sh s2276_m5_keyon_pointer_branch
```

The script must stage both port and retail arms before launch, self-watchdog
each arm, SIGKILL only after its bounded phase deadline, and write bounded
summaries under `scratch/agent/s2276_m5_keyon_pointer_branch/`. Do not infer
audio/output behavior from this unit; it is a key-on contract comparison.
