# S4216 — reconciling the s4212-s4215 data_ptr thread with the s3482-s3486 retail evidence

The s4212-s4215 chain concluded "OSTask.data_ptr points at a menu-owned heap
block, so the builder targets the wrong block" (H-builder-wrong-target). The
retail oracle evidence from s3482/s3483/s3486 (PORTING-STATE.md ~line 132304)
already answers the writer question and contradicts that reading:

| Fact | Source |
|---|---|
| data_ptr (0x1494A0) is stored by guest PC 0x8009177C, size by 0x80091784; selector pointer by 0x80091074 | s3482, s3483, s3486 (oracle + port, same PCs) |
| RETAIL stores only 0x80171CE0 / 0x80173B20 (size 1-2) at those PCs in title phase | s3483 oracle, 629 rows |
| Those are the same 7728 B guest-heap pairs s4212 found at phase entry | s4212 |

So the pointer-to-a-7728-B-heap-block is what the retail game does too. It is
not evidence of a wrong target, and the writer is already named. The only
retail/port divergence recorded at this boundary is extra port operands
(0x8018DD30/size 3, 0x8018FB70/size 1; s3482/s3483), while s3486's fixed retry
saw only one 0x8018DD30 and no 0x8018FB70.

Status of hypotheses: H-builder-wrong-target REFUTED (retail does the same
store). H-builder-skipped REFUTED (the builder store PCs execute in the port).
H-ucode-uses-other-ptr remains open. Single caveat: s4214's block *content*
(ASCII names + 0x28-stride pointer structs) was never compared with retail,
so "the content is not an audio command list" is a port-only observation.

Discriminating next measurement: dump the 7728 B block at 0x80171CE0 in the
RETAIL oracle (tools/oracle, whole-RDRAM control first) at the same title phase
and compare record 0 / ASCII fraction against the port s4214 scan. Same shape
=> block content is legitimate and the divergence lies in ucode consumption or
output (not input); different => the content producer diverges.
