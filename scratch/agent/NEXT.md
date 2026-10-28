# NEXT: RESUME — map the actual HUD SIGBUS instruction before adding another witness
HYPOTHESIS-ID: g1c-dd-phase2

Checkpoint close-out: the prior attempt stopped before completing this unit;
do not rerun the experiment. Resume with one bounded offline work unit: map the saved dd4 crash PC
`hudDisplayUpdateWorker+5532` to the exact generated guest instruction and
source file, then enumerate the pointer-producing loads immediately before it.

Competing hypotheses:
- H-overlay-alias: the local symbol/offset names the wrong overlay body.
- H-other-generated-load: another generated `MEM_*` site supplies the bad
  `0x951335B0` pointer; the s6595 `0x80049644/54` witness was simply the wrong
  load chain.
- H-host-deref: generated code supplies a value, but host/runtime code performs
  the faulting dereference after the load.
- H-stale: the correctly mapped site reads a stale object whose lifetime differs
  between retail and dd4.

Discriminator: use the captured crash PC and binary symbols/disassembly (`nm`,
`atos`, `llvm-objdump`/`otool`) to classify the faulting instruction. A generated
load selects H-other-generated-load or H-stale and gets one focused witness with
the existing `[hudptrw]` player-record positive control; a host instruction
selects H-host-deref and gets a host-side input/writer trace; an address/body
mismatch selects H-overlay-alias. Do not add a guard or skip.

Resume artifacts: `scratch/agent/s6595_ret_outer*.log` and
`scratch/agent/s6595_dd4_outer*.log` are present; the corrected s6595 result is
already recorded in `PORTING-STATE.md`. Exact checks before any build:
`grep -n -A8 -B8 'pc-symbol.*hudDisplayUpdateWorker+5532' scratch/agent/m6/g1_lvl7s6591_dd4/run.log`
`nm -an build/RogueSquadron64Recomp | rg 'hudDisplayUpdateWorker|transformWorldPosToGridSpace'`
`otool -tvV build/RogueSquadron64Recomp | rg -n -C4 '951335|80049644|80049654'`

If the mapped site is generated, add the persistent fixup before rebuilding and
rerun `zsh scratch/agent/s6591_run.sh ret` and `zsh scratch/agent/s6591_run.sh dd4`
with the same envs. The oracle remains unavailable until its missing
`libmupen64plus.dylib` core/plugin is installed; do not treat runtime output as
independent retail ground truth.
