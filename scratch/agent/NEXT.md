# Next: offline audit of the delay-slot/branch-register-hazard idiom class (M3)

PatchesLib fresh-source qualification is dropped from the critical path (open
dependency: mips64-elf-gcc/ld, see CURRENT-TRUTH). This unit needs no toolchain
and no game run.

Idiom class NOT in the CURRENT-TRUTH closed list: a branch/jr/jalr whose delay
slot writes a register that the branch condition, target, or link value reads
(MIPS reads the branch operands BEFORE the slot executes), plus delay slots that
write $ra for jal/jalr. N64Recomp should latch operands first; verify on the
generated code rather than assume.

Hypotheses:
- H1: N64Recomp latches branch operands before the slot in every generated site
  (class closed).
- H2: some sites emit slot-then-test and read the clobbered value (real bug).
- H3: sites exist but are statically unreachable/data (no impact).

Discriminator: scan the ROM disassembly (or RecompiledFuncs) for branches whose
slot instruction's destination register equals a branch source register; for N
sites found, read the generated C and check the ordering. Same-run positive
control: at least one known-hazard site must be located and its generated C
shown to latch correctly (or not). Report count / total branches as a
denominator. Do not touch lib/.

HYPOTHESIS-ID: delay-slot-operand-hazard-audit
