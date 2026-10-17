# Next: audit the "branch/jump inside a delay slot" idiom class (M3)

Delay-slot operand hazard closed in s5345. Next unaudited class: a branch or
jump whose delay slot is itself a branch/jump (undefined on MIPS; compilers
avoid it, but hand-written libultra/asm may not), plus branch-likely slots
that are loads/stores with side effects when untaken.

Hypotheses: H1 zero such sites in the main ELF (class closed trivially);
H2 sites exist and N64Recomp emits something other than the hardware
behaviour; H3 sites exist only in libultra functions replaced by the runtime.
Discriminator: extend tools/audit_delay_slot_hazard.py to list branch/jump
whose next instruction is a branch/jump; report count/38,033; for any site,
read the generated C. Positive control: synthetic input list containing a
branch-in-slot must be flagged. Do not touch lib/. If zero sites, close the
class and pick the next idiom (e.g. jal-in-slot of jr, or lwl/lwr pairs
straddling a branch target).

HYPOTHESIS-ID: delay-slot-branch-in-slot-audit
