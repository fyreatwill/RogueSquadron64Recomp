# lv0 class-1 objective targets (s5850; from m6/s5849i run.log via tools/dump_lv0_objective_targets.py)
Win arm c1>=21 == tear down ALL 21 distinct descriptors below (each +0x74 delta=1). K = torn down in the 723 s invuln hold; the TELE_BOLT run s5846 tore down 17 of the same 21. grp = descriptor +0x80 second counter index (110-114). pos = descriptor words 4-6 as floats (frame unverified).

```
distinct class-1 descriptors: 21, torn down (counter-1 sets): 8
desc      boolid kill spawns grp  posx posy posz
8031BBC8  0x18  K  1  110  51 -6 34
8031BE74  0x19  K  1  110  51 -6 43
8031BF68  0x1b  K  1  112  109 -4 37
8031C05C  0x1c  K  2  112  91 -6 40
8031C150  0x1d  K  2  112  104 -5 54
803175A4  0x1f  -  4  110  37 -2 35
8031A99C  0x20  -  4  111  68 -3 22
8031AA94  0x21  -  4  111  70 -3 23
80317698  0x22  -  4  113  45 -1 85
8031ADDC  0x23  -  5  113  52 -2 92
80317888  0x24  -  4  114  36 -3 112
80317790  0x25  -  4  114  64 -2 118
8031AED4  0x26  -  3  112  102 0 36
8031AFCC  0x27  -  4  112  94 0 44
8031C244  0x28  -  4  111  71 -4 27
8031C338  0x29  K  3  111  75 -5 26
8031C42C  0x2a  K  3  111  76 -4 20
8031C520  0x2b  K  1  111  58 -5 26
8031C614  0x2d  -  4  113  45 -5 81
8031C708  0x2e  -  5  113  47 -2 94
8031C7FC  0x2f  -  5  113  55 -4 91
```

## class-2 NPC positions vs nearest class-1 descriptor (s5887, single run m6/s5887_pos; npc+0/+8 = x/z at msg=3 of [npcd])
80319a9c (37,36) <-> 803175a4 (37,35) | 80319cdc (69,23) <-> 8031aa94 (70,23) | 80319e5c (91,42) <-> 8031c05c (91,40)
8031a5dc (47,83) <-> 80317698 (45,85) | 8031a69c (51,91) <-> 8031addc (52,92) | 80319b5c (34,113) <-> 80317888 (36,112) | 80319c1c (62,118) <-> 80317790 (64,118)
All 7/7 class-2 objects sit within ~2 units (xz) of a class-1 descriptor.
