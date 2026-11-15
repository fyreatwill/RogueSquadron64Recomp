# NEXT (s7405)
HYPOTHESIS-ID: cop-control-register-access

s7404 closed class BN (direct RCP/PI register access, H-none: all hits in N64Recomp ignored_funcs). Work unit, class BO:
LIVE guest code that touches coprocessor CONTROL state directly - `ctc1/cfc1 $31` (FCSR: rounding mode, flush-to-zero,
exception enables), `mfc0/mtc0` (Count, Compare, Status/IE, Cause) - bypassing the replaced libultra (osGetCount etc).
/tmp/s7392.dis has 54 mfc0/mtc0 lines; 27 ctc1/cfc1 lines.
1. New tools/s7405_cop_access.py: enumerate ctc1/cfc1/mfc0/mtc0 per function, tag LIVE/REPLACED/IGNORED/dead (copy the
   ignored() loader from tools/s7404_rcp_access.py - s7401 live() alone treats ignored_funcs as live). For ctc1 rows, constant-
   propagate the value written (rounding mode bits 0-1, FS bit 24).
2. For each live row: what N64Recomp emits (grep ../N64Recomp/RecompiledFuncs for the function: ctc1 -> rounding-mode set? or
   dropped; mfc0 Count -> host counter or 0) vs hardware.
3. Hypotheses: H-none (no live row, or each emitted equivalently), H-fcsr (a live ctc1 sets a non-default rounding mode / FS
   that the recomp ignores -> float results differ: cvt/trunc/round paths), H-count (a live mfc0 Count read returns a constant
   or wrong-rate value -> timing/rand seeds). Static first; runtime only for a live divergent row: one counter + planted control,
   two arms only if a fix lands (default-on env, =0 old).
