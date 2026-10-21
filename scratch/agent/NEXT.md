# NEXT: what value is written to sp+0x175 before bit 0x8?

s5779 closed the caller. Do not retag the two jals. Do not change
`ROGUESQ_ALT_HOLD`. Do not log another orientation angle.

`updatePlayerCraftPhysics` takes the bit-0x8 jal at 0x800B2A58 when its
float is <= 0 and byte sp+0x175 != 0. That byte is not stored in the
caller. The only writer is `sb $v0, 0x0($v1)` at 0x800FFC60 in
`stepObjectOrientationTowardTarget` (funcs_43.c). It copies `lbu 0($s0)`
from the array at sp+0x198, stride 0x2C, index = word at sp+0x488, and
only when byte sp+0x497 != 0. The caller never zeroes sp+0x175, so a
nonzero stack leftover can still select the jal.

One build, one run. Add a fixup hooked from
`tools/fixup_game_funcs_vendored.py` (same shape as
`tools/apply_s5779_bit8_caller.py`). Do not hand-edit `funcs_43.c`.
At the 0x800FFC60 store, when the saved object (word at sp+0x4F8, the
incoming a0) is 0x80137DBC, log: index, source byte, flag byte
sp+0x497. Print every player store whose source byte != 0 (cap 40) and
the first few flag!=0 stores. Leave `[bit8call]` in place. Reuse
`scratch/agent/s5777_althold.sh` unchanged. Screen must not show
`CGSSessionScreenIsLocked=Yes`. Preserve the current
`scratch/agent/m6/s5777_althold/run.log` before the run overwrites it.

Control: a `[bit8call]` line `site=0x800B2A58 a0=0x80137DBC hw=0x0001`
still prints, and the new store line is judged against that same
death. Zero store lines in front of a firing bit8call is a result only
if the store log's own positive control fired earlier in the run
(a player store line, or a flag!=0 line). A run with no bit8call
0x0001 transition is void.

- H-written-const: every such bit8call is preceded by this sb, flag
  != 0, and the source byte is the same small value each time. The
  byte is an impact flag. Next is the float<=0 test, not the byte.
- H-written-vary: every such bit8call is preceded by this sb, flag
  != 0, and the source byte takes more than one nonzero value. Next
  is what record+0 means.
- H-stale: a bit8call hw=0x0001 has no sb from this call in front of
  it. The stack byte was leftover. Next is who last wrote that slot,
  not the table.

HYPOTHESIS-ID: g1-sp175-src
