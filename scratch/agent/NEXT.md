# Next work unit
HYPOTHESIS-ID: m3-unclosed-idiom-census
Goal: list M3 idiom classes NOT in CURRENT-TRUTH "M3 and rendering" closed list (trap/break/syscall/cop0, unaligned, LL/SC/cache, div, float conv/cmp/FCSR, mem-width, indirect calls, self walks, branch-likely, var shifts, HI/LO, 64-bit shifts, 32-bit mult, movz/movn).
Method: one pass over RecompiledFuncs/ grepping for helper/do_break/unimplemented emitters; count sites per class (denominators). Candidates: COP1 ldc1/sdc1 alignment, cvt rounding modes, trunc.l, mfc1/dmfc1 width, sltiu sign-extension, jr with non-ra reg in delay slot.
Outcomes: class with >0 unguarded sites -> classify each, guard or prove dead (commit a guard in fixup script); all zero -> close and note in CURRENT-TRUTH, then resume renaming preflight.
Do not re-run VI-640 soaks.
