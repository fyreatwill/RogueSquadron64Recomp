# Next work unit
HYPOTHESIS-ID: retail-entry-revisit
M3 idiom census is exhausted (s4975-s4977). M5 and renaming are parked/exhausted per CURRENT-TRUTH.
Work unit: REVISIT the external retail-entry boundary (old target PC 0x800903f0) with a NEW angle, not the Rice route again.
Candidate angles (pick ONE; write 2-4 hypotheses + discriminator first): (1) oracle watch on retail ROM for writers of the function-pointer slot that reaches 0x800903f0, not the PC itself; (2) static xref of 0x800903f0 callers/data refs in the ELF to see if reachable only via overlay load; (3) compare s4844 oracle VI origin sequence against ours.
Positive control first (whole-RDRAM watch must fire). If no new angle can be named, go BLOCKED with a specific question.
Do not re-run VI-640 soaks.
