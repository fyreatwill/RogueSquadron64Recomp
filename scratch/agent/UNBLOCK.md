# UNBLOCK (s4969) — route 3 (re-scope); the block was not an owner decision
Block (s4968): "pivot targets exhausted; owner must pick (1) movz/movn in N64Recomp, (2) declare M5 done/new goal, (3) resume parked."

Route 1 (refute): option (1) is not a human decision. docs/CURRENT-TRUTH.md Next-steps item 5 already calls conditional-move support "a separate engineering task". N64Recomp is a maintained local tree; grep of its src/ and include/ finds no movz/movn handling (only rabbitizer decodes the opcode). No install/spend/security boundary is involved. Declaring M5 done stays the owner's call and is not needed.
Route 2: not applicable (nothing missing).
Route 3 taken: NEXT.md rewritten to implement movz/movn in N64Recomp, validated in a scratch regen first.
Route 4 not needed: a loop-continuable unit exists.
Caveat: the defect is dormant (2 of 149 reachable sites are data-as-code), so no runtime change is expected; the unit closes the last recompiler defect with a census-verified result.
