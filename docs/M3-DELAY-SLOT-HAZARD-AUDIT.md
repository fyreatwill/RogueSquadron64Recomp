# M3 idiom-class audit: delay-slot operand hazard (Session 5345)

Class: a branch/jump whose delay-slot instruction writes a GPR that the
branch reads (condition operand, `jr`/`jalr` target) or that `jal`/`jalr`/`bal`
link. MIPS reads branch operands before the slot executes, so recompiled code
must evaluate the condition first.

Tool: `tools/audit_delay_slot_hazard.py <elf> <out>` (census from
`mips-linux-gnu-objdump -d -M no-aliases`; run on
`rogue_squadron64/build/roguesquadron.elf`). `tools/audit_delay_slot_gen.py
<sites> <RecompiledFuncs dir>` checks the generated C (post-fixup,
`N64Recomp/RecompiledFuncs/funcs_*.c`) for condition-before-slot ordering.

Denominators: 302,115 instructions; 38,033 branch/jump sites with a slot;
3,105 hazard sites (8.2%): beq 1725, bne 1317, blez 30, bltz 20, bgtz 8,
bgez 5. Zero `jr`/`jalr` target clobbers, zero link-register clobbers, zero
branch-likely hazard sites.

Result: 3,085 of 3,105 sites are emitted as `if (cond) { slot; goto }` with
the condition ahead of any `ctx->rN =` write; 0 are slot-first. The other 20
have no generated body because they lie in libultra `os*` functions
(osAiSetFrequency, __osInsertTimer, osRecvMesg, osSendMesg, osStartThread,
osJamMesg, osEepromProbe/Write, osVirtualToPhysical, __osLeoResume) supplied
by N64ModernRuntime. 66 sites carry a diagnostic store
(`g_rs64_last_guest_pc`, `rs64_m5_selector_tick_edge`) before the `if (`; a
12-line rescan found the `if (` ahead of any register write in all of them.

Positive control: the ordering classifier returns `SLOT-FIRST` on a synthetic
slot-before-`if` body and `ok` on the correct one. The census located
`loadOverlay` 0x80000B60 (`beq s0,v0` with `lui v0` slot); its generated C
compares first, then runs the `lui` inside the taken arm and again after.

Verdict: H1 (operands latched before slot) holds at 3,085/3,085 generated
sites; H2 refuted; H3 not needed. Class closed. ORIGIN: no guard added.
Limit: only the main-ELF text was audited; RSP-ucode and overlay-loaded code
paths use separate generators and are not covered.
