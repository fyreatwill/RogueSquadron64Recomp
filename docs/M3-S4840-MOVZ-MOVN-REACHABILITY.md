# M3 `movz`/`movn` generated-C reachability classification

## Method

The 149 unique file/guest-PC sites from the s4840 census were classified by a guest-instruction CFG over each containing generated function. The first instruction is the entry; ordinary fall-through and branch targets are followed, and `jr`/`jalr` retain only their delay slot with no statically known successor. Duplicate emitted copies are grouped by file and guest PC. This is a static generated-C result, not runtime reachability.

## Result

| classification | sites |
|---|---:|
| reachable | 2 |
| post-return/unreachable | 16 |
| data-like/unreachable | 131 |

## Site table

| file | guest PC | op/dest | copies | classification | predecessor evidence |
|---|---:|---|---:|---|---|
| funcs_27.c | `0x8009F020` | movz $zero, movz $zero | 2 | data-like/unreachable | line 8657 predecessor .word       0x03080808                   # jr          $t8 # 00080800 <InstrIdType: CPU_SPECIAL>; line 8661 predecessor movz        $zero, $at, $t8 |
| funcs_27.c | `0x8009F124` | movz $zero | 1 | data-like/unreachable | line 8792 predecessor nop |
| funcs_27.c | `0x8009F60C` | movz $zero | 1 | data-like/unreachable | line 9968 predecessor srlv        $zero, $s3, $at |
| funcs_27.c | `0x8009F744` | movz $zero | 1 | post-return/unreachable | line 10130 predecessor .word       0x0033000C                   # syscall     0 # 00330000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x8009F878` | movz $zero | 1 | data-like/unreachable | line 10291 predecessor tgei        $t8, 0x703 |
| funcs_27.c | `0x8009F9B0` | movz $zero | 1 | data-like/unreachable | line 10453 predecessor .word       0x05070707                   # INVALID     $t0, $a3, 0x707 # 00000000 <InstrIdType: CPU_REGIMM> |
| funcs_27.c | `0x8009FCF4` | movz $zero | 1 | post-return/unreachable | line 11277 predecessor lb          $v1, -0x3904($zero) |
| funcs_27.c | `0x8009FCFC` | movn $zero | 1 | data-like/unreachable | line 11281 predecessor lb          $v1, -0x3910($zero) |
| funcs_27.c | `0x8009FEF4` | movz $zero | 1 | post-return/unreachable | line 11541 predecessor lb          $v1, -0x3BF0($zero) |
| funcs_27.c | `0x8009FEFC` | movn $zero | 1 | data-like/unreachable | line 11545 predecessor lb          $v1, -0x3BFC($zero) |
| funcs_27.c | `0x8009FFF4` | movn $zero | 1 | data-like/unreachable | line 11671 predecessor .word       0x00080009                   # jalr        $zero, $zero # 00080000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A0098` | movz $zero, movz $zero | 2 | data-like/unreachable | line 11752 predecessor .word       0x00470048                   # jr          $v0 # 00070040 <InstrIdType: CPU_SPECIAL>; line 11756 predecessor .word       0x0049004A                   # movz        $zero, $v0, $t1 # 00000040 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A0154` | movn $zero | 1 | data-like/unreachable | line 11851 predecessor nop |
| funcs_27.c | `0x800A0208` | movz $zero, movz $zero | 2 | data-like/unreachable | line 11940 predecessor .word       0x00C700C8                   # jr          $a2 # 000700C0 <InstrIdType: CPU_SPECIAL>; line 11944 predecessor .word       0x00C900CA                   # movz        $zero, $a2, $t1 # 000000C0 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A029C` | movz $zero, movz $zero | 2 | data-like/unreachable | line 12018 predecessor .word       0x01070108                   # jr          $t0 # 00070100 <InstrIdType: CPU_SPECIAL>; line 12022 predecessor .word       0x0109010A                   # movz        $zero, $t0, $t1 # 00000100 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A0384` | movn $zero | 1 | data-like/unreachable | line 12139 predecessor .word       0x01480149                   # jalr        $zero, $t2 # 00080140 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A0448` | movn $zero | 1 | data-like/unreachable | line 12237 predecessor .word       0x00000189                   # jalr        $zero, $zero # 00000180 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A04E0` | movz $zero, movz $zero | 2 | data-like/unreachable | line 12312 predecessor .word       0x01C701C8                   # jr          $t6 # 000701C0 <InstrIdType: CPU_SPECIAL>; line 12316 predecessor .word       0x01C901CA                   # movz        $zero, $t6, $t1 # 000001C0 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A0590` | movn $zero | 1 | data-like/unreachable | line 12405 predecessor .word       0x02080209                   # jalr        $zero, $s0 # 00080200 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A0FD4` | movn $zero | 1 | post-return/unreachable | line 13890 predecessor .word       0x0178017E                   # dsrl32      $zero, $t8, 5 # 01600000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A1064` | movz $zero | 1 | post-return/unreachable | line 13966 predecessor .word       0x0337033D                   # INVALID     $t9, $s7, 0x33D # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A17B0` | movn $zero | 1 | data-like/unreachable | line 98942 predecessor .word       0x006B0075                   # INVALID     $v1, $t3, 0x75 # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A1A2C` | movz $v0, movz $v0 | 2 | data-like/unreachable | line 99620 predecessor .word       0x00000E08                   # jr          $zero # 00000E00 <InstrIdType: CPU_SPECIAL>; line 99624 predecessor movz        $v0, $zero, $zero |
| funcs_27.c | `0x800A1A6C` | movn $v0 | 1 | data-like/unreachable | line 99664 predecessor jalr        $v0, $zero |
| funcs_27.c | `0x800A1AA8` | movz $v0, movz $v0 | 2 | data-like/unreachable | line 99701 predecessor .word       0x00000E08                   # jr          $zero # 00000E00 <InstrIdType: CPU_SPECIAL>; line 99705 predecessor .word       0x0000110A                   # movz        $v0, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A1AE8` | movn $v0 | 1 | data-like/unreachable | line 99746 predecessor jalr        $v0, $zero |
| funcs_27.c | `0x800A1B24` | movz $v0, movz $v0 | 2 | data-like/unreachable | line 99784 predecessor .word       0x00000E08                   # jr          $zero # 00000E00 <InstrIdType: CPU_SPECIAL>; line 99788 predecessor .word       0x0000110A                   # movz        $v0, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A1B64` | movn $v0 | 1 | data-like/unreachable | line 99829 predecessor .word       0x00000F09                   # jalr        $at, $zero # 00000700 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A1BA0` | movz $v0 | 1 | data-like/unreachable | line 99867 predecessor .word       0x00000E07                   # srav        $at, $zero, $zero # 00000600 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A1BE0` | movn $v0, movn $v0, movn $v0, movn $v0 (+1 copies) | 5 | data-like/unreachable | line 99904 predecessor .word       0x00000E08                   # jr          $zero # 00000E00 <InstrIdType: CPU_SPECIAL>; line 99917 predecessor .word       0x00000E08                   # jr          $zero # 00000E00 <InstrIdType: CPU_SPECIAL>; line 99927 predecessor .word       0x00000E08                   # jr          $zero # 00000E00 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A1C50` | movz $zero | 1 | data-like/unreachable | line 100011 predecessor sd          $ra, -0x21EE($ra) |
| funcs_27.c | `0x800A1C54` | movz $zero | 1 | data-like/unreachable | line 100013 predecessor .word       0x0000020A                   # movz        $zero, $zero, $zero # 00000200 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A1C58` | movz $at | 1 | data-like/unreachable | line 100015 predecessor .word       0x0000070A                   # movz        $zero, $zero, $zero # 00000700 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A1C5C` | movz $v0 | 1 | data-like/unreachable | line 100017 predecessor .word       0x00000C0A                   # movz        $at, $zero, $zero # 00000400 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A1C90` | movn $zero | 1 | data-like/unreachable | line 100051 predecessor sd          $ra, -0x25ED($ra) |
| funcs_27.c | `0x800A1C94` | movn $zero | 1 | data-like/unreachable | line 100053 predecessor .word       0x0000020B                   # movn        $zero, $zero, $zero # 00000200 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A1C98` | movn $at | 1 | data-like/unreachable | line 100055 predecessor .word       0x0000070B                   # movn        $zero, $zero, $zero # 00000700 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A1C9C` | movn $v0 | 1 | data-like/unreachable | line 100057 predecessor .word       0x00000D0B                   # movn        $at, $zero, $zero # 00000500 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2A2C` | movz $t7, movz $t7 | 2 | data-like/unreachable | line 102249 predecessor .word       0x00198E48                   # jr          $zero # 00198E40 <InstrIdType: CPU_SPECIAL>; line 102253 predecessor .word       0x001D7C4A                   # movz        $t7, $zero, $sp # 00000440 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2A6C` | movn $t5 | 1 | data-like/unreachable | line 102295 predecessor .word       0x001C1B49                   # jalr        $v1, $zero # 001C0340 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2AA8` | movz $sp, movz $sp | 2 | data-like/unreachable | line 102333 predecessor .word       0x001A2848                   # jr          $zero # 001A2840 <InstrIdType: CPU_SPECIAL>; line 102337 predecessor .word       0x001EEA4A                   # movz        $sp, $zero, $fp # 00000240 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2AE8` | movn $zero | 1 | data-like/unreachable | line 102378 predecessor .word       0x001CC649                   # jalr        $t8, $zero # 001C0640 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2B24` | movz $s4, movz $s4 | 2 | data-like/unreachable | line 102415 predecessor .word       0x0019E648                   # jr          $zero # 0019E640 <InstrIdType: CPU_SPECIAL>; line 102419 predecessor .word       0x001FA74A                   # movz        $s4, $zero, $ra # 00000740 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2B64` | movn $k0 | 1 | data-like/unreachable | line 102461 predecessor .word       0x001C7E49                   # jalr        $t7, $zero # 001C0640 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2BA0` | movz $t2 | 1 | data-like/unreachable | line 102499 predecessor .word       0x00186047                   # srav        $t4, $t8, $zero # 00000040 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2BE0` | movn $t7, movn $t7, movn $t7, movn $t7 (+1 copies) | 5 | data-like/unreachable | line 102536 predecessor .word       0x001ACF48                   # jr          $zero # 001ACF40 <InstrIdType: CPU_SPECIAL>; line 102549 predecessor .word       0x001ACF48                   # jr          $zero # 001ACF40 <InstrIdType: CPU_SPECIAL>; line 102559 predecessor .word       0x001ACF48                   # jr          $zero # 001ACF40 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2C50` | movz $s4 | 1 | data-like/unreachable | line 102645 predecessor sd          $zero, -0x33AE($fp) |
| funcs_27.c | `0x800A2C54` | movz $gp | 1 | data-like/unreachable | line 102647 predecessor .word       0x0004A24A                   # movz        $s4, $zero, $a0 # 00000240 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2C58` | movz $a1 | 1 | data-like/unreachable | line 102649 predecessor .word       0x000DE74A                   # movz        $gp, $zero, $t5 # 00000740 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2C5C` | movz $t6 | 1 | data-like/unreachable | line 102651 predecessor .word       0x00172C4A                   # movz        $a1, $zero, $s7 # 00000440 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2C90` | movn $v1 | 1 | data-like/unreachable | line 102687 predecessor sd          $k0, 0x7A53($sp) |
| funcs_27.c | `0x800A2C94` | movn $t1 | 1 | data-like/unreachable | line 102689 predecessor .word       0x0005194B                   # movn        $v1, $zero, $a1 # 00000140 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2C98` | movn $t7 | 1 | data-like/unreachable | line 102691 predecessor .word       0x000F4B4B                   # movn        $t1, $zero, $t7 # 00000340 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A2C9C` | movn $s6 | 1 | data-like/unreachable | line 102693 predecessor .word       0x00197E4B                   # movn        $t7, $zero, $t9 # 00000640 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A326C` | movz $s5 | 1 | data-like/unreachable | line 104165 predecessor and         $t9, $zero, $at |
| funcs_27.c | `0x800A3278` | movz $t5 | 1 | data-like/unreachable | line 104171 predecessor .word       0x00017F91                   # mthi        $zero # 00017F80 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3280` | movz $t0 | 1 | data-like/unreachable | line 104175 predecessor dsll        $t2, $at, 22 |
| funcs_27.c | `0x800A33A0` | movz $zero | 1 | data-like/unreachable | line 104321 predecessor .word       0x00000557                   # dsrav       $zero, $zero, $zero # 00000540 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A343C` | movz $t4 | 1 | data-like/unreachable | line 104399 predecessor .word       0x00106141                   # INVALID     $zero, $s0, 0x6141 # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3558` | movz $t7 | 1 | data-like/unreachable | line 104541 predecessor .word       0x001176C1                   # INVALID     $zero, $s1, 0x76C1 # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A35A8` | movn $t9 | 1 | data-like/unreachable | line 104584 predecessor dsubu       $t9, $zero, $s1 |
| funcs_27.c | `0x800A362C` | movz $t2 | 1 | data-like/unreachable | line 104650 predecessor .word       0x001251CE                   # INVALID     $zero, $s2, 0x51CE # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3648` | movz $t6 | 1 | data-like/unreachable | line 104664 predecessor .word       0x00126F87                   # srav        $t5, $s2, $zero # 00000780 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A367C` | movz $s5 | 1 | data-like/unreachable | line 104690 predecessor dsrl        $s4, $s2, 28 |
| funcs_27.c | `0x800A36D8` | movz $at | 1 | data-like/unreachable | line 104736 predecessor .word       0x00130B63                   # negu        $at, $s3 # 00000340 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A37A0` | movn $fp | 1 | data-like/unreachable | line 104839 predecessor tge         $zero, $s3, 945 |
| funcs_27.c | `0x800A37D4` | movn $a1 | 1 | data-like/unreachable | line 104865 predecessor .word       0x001428A2                   # sub         $a1, $zero, $s4 # 00000080 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3804` | movz $t4 | 1 | data-like/unreachable | line 104893 predecessor .word       0x001460D4                   # dsllv       $t4, $s4, $zero # 000000C0 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3884` | movn $ra | 1 | data-like/unreachable | line 104957 predecessor tlt         $zero, $s4, 998 |
| funcs_27.c | `0x800A3900` | movz $s2 | 1 | data-like/unreachable | line 105019 predecessor .word       0x0015920E                   # INVALID     $zero, $s5, -0x6DF2 # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3914` | movz $s6 | 1 | post-return/unreachable | line 105032 predecessor .word       0x0015AB07                   # srav        $s5, $s5, $zero # 00000300 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3954` | movn $zero | 1 | data-like/unreachable | line 105064 predecessor tne         $zero, $s5, 1006 |
| funcs_27.c | `0x800A3A94` | movn $s4 | 1 | data-like/unreachable | line 105230 predecessor .word       0x0017A114                   # dsllv       $s4, $s7, $zero # 00000100 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3AF0` | movz $a0 | 1 | data-like/unreachable | line 105282 predecessor tne         $zero, $t8, 127 |
| funcs_27.c | `0x800A3B2C` | movn $t7 | 1 | data-like/unreachable | line 105316 predecessor .word       0x00187424                   # and         $t6, $zero, $t8 # 00000400 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3C64` | movz $t0 | 1 | data-like/unreachable | line 105477 predecessor dsrl        $a3, $k0, 18 |
| funcs_27.c | `0x800A3C7C` | movn $t4 | 1 | data-like/unreachable | line 105489 predecessor tlt         $zero, $k0, 388 |
| funcs_27.c | `0x800A3CE0` | movz $zero | 1 | data-like/unreachable | line 105539 predecessor .word       0x001AFB4E                   # INVALID     $zero, $k0, -0x4B2 # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3CF0` | movn $v1 | 1 | post-return/unreachable | line 105556 predecessor .word       0x001B1449                   # jalr        $v0, $zero # 001B0440 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3D58` | movz $s7 | 1 | data-like/unreachable | line 105608 predecessor .word       0x001BB8E1                   # addu        $s7, $zero, $k1 # 000000C0 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3E34` | movn $a1 | 1 | data-like/unreachable | line 105720 predecessor .word       0x001D220F                   # sync # 001D2200 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3E44` | movz $t0, movz $t0 | 2 | post-return/unreachable | line 105730 predecessor .word       0x001D3D08                   # jr          $zero # 001D3D00 <InstrIdType: CPU_SPECIAL>; line 105734 predecessor .word       0x001D43CA                   # movz        $t0, $zero, $sp # 000003C0 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3E70` | movz $s1 | 1 | data-like/unreachable | line 105756 predecessor tne         $zero, $sp, 542 |
| funcs_27.c | `0x800A3F08` | movn $s2 | 1 | data-like/unreachable | line 105835 predecessor dsra        $s1, $fp, 29 |
| funcs_27.c | `0x800A3F50` | movn $v0 | 1 | data-like/unreachable | line 105875 predecessor .word       0x001F0F9D                   # dmultu      $zero, $ra # 00000F80 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A3F64` | movn $a3 | 1 | data-like/unreachable | line 105885 predecessor .word       0x001F3394                   # dsllv       $a2, $ra, $zero # 00000380 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4190` | movn $t7 | 1 | data-like/unreachable | line 106168 predecessor .word       0x000E7CE3                   # negu        $t7, $t6 # 000004C0 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A41DC` | movz $a3 | 1 | data-like/unreachable | line 106206 predecessor .word       0x000E3DD4                   # dsllv       $a3, $t6, $zero # 000005C0 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4258` | movz $k0 | 1 | data-like/unreachable | line 106268 predecessor .word       0x000DD93D                   # INVALID     $zero, $t5, -0x26C3 # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A42AC` | movz $s2 | 1 | data-like/unreachable | line 106311 predecessor .word       0x000D96AD                   # daddu       $s2, $zero, $t5 # 00000680 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A448C` | movz $a1 | 1 | data-like/unreachable | line 106562 predecessor .word       0x000C319B                   # divu        $a2, $zero, $t4 # 00000180 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4514` | movz $k0 | 1 | data-like/unreachable | line 106634 predecessor .word       0x000BD345                   # INVALID     $zero, $t3, -0x2CBB # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A45B4` | movn $t4 | 1 | data-like/unreachable | line 106719 predecessor .word       0x000B67EE                   # dsub        $t4, $zero, $t3 # 000007C0 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A45CC` | movz $t2 | 1 | post-return/unreachable | line 106737 predecessor .word       0x000B5829                   # INVALID     $zero, $t3, 0x5829 # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4684` | movn $k1 | 1 | data-like/unreachable | line 106838 predecessor .word       0x000AE20E                   # INVALID     $zero, $t2, -0x1DF2 # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A46B0` | movn $t8 | 1 | data-like/unreachable | line 106863 predecessor .word       0x000AC689                   # jalr        $t8, $zero # 000A0680 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A48A8` | movn $s3 | 1 | data-like/unreachable | line 107121 predecessor sra         $s3, $t1, 24 |
| funcs_27.c | `0x800A48F8` | movz $t5 | 1 | data-like/unreachable | line 107162 predecessor .word       0x000971F9                   # INVALID     $zero, $t1, 0x71F9 # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4A34` | movn $t9 | 1 | data-like/unreachable | line 107333 predecessor .word       0x0008CB93                   # mtlo        $zero # 0008CB80 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4A70` | movn $s5 | 1 | post-return/unreachable | line 107365 predecessor .word       0x0008AD4C                   # syscall     693 # 00080000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4A74` | movz $s5 | 1 | post-return/unreachable | line 107367 predecessor .word       0x0008AB4B                   # movn        $s5, $zero, $t0 # 00000340 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4A78` | movz $s4 | 1 | post-return/unreachable | line 107369 predecessor .word       0x0008A94A                   # movz        $s5, $zero, $t0 # 00000140 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4A7C` | movn $s4 | 1 | post-return/unreachable | line 107371 predecessor .word       0x0008A74A                   # movz        $s4, $zero, $t0 # 00000740 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4A80` | movn $s4 | 1 | data-like/unreachable | line 107373 predecessor .word       0x0008A54B                   # movn        $s4, $zero, $t0 # 00000540 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4B28` | movz $t2 | 1 | data-like/unreachable | line 107461 predecessor .word       0x000852F7                   # INVALID     $zero, $t0, 0x52F7 # 00000000 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4B40` | movn $t0 | 1 | data-like/unreachable | line 107474 predecessor teq         $zero, $t0, 285 |
| funcs_27.c | `0x800A4B8C` | movn $a0 | 1 | data-like/unreachable | line 107512 predecessor .word       0x0008236C                   # dadd        $a0, $zero, $t0 # 00000340 <InstrIdType: CPU_SPECIAL> |
| funcs_27.c | `0x800A4B9C` | movz $v1 | 1 | data-like/unreachable | line 107520 predecessor .word       0x00081BEA                   # slt         $v1, $zero, $t0 # 000003C0 <InstrIdType: CPU_SPECIAL> |
| funcs_37.c | `0x800CC938` | movn $zero | 1 | data-like/unreachable | line 6959 predecessor .word       0x00C000A0                   # add         $zero, $a2, $zero # 00000080 <InstrIdType: CPU_SPECIAL> |
| funcs_37.c | `0x800CC9F8` | movn $zero | 1 | data-like/unreachable | line 7057 predecessor .word       0x00060009                   # jalr        $zero, $zero # 00060000 <InstrIdType: CPU_SPECIAL> |
| funcs_37.c | `0x800CCA1C` | movn $zero | 1 | data-like/unreachable | line 7076 predecessor .word       0x008A0000                   # sll         $zero, $t2, 0 # 00800000 <InstrIdType: CPU_SPECIAL> |
| funcs_37.c | `0x800CCA20` | movn $zero | 1 | data-like/unreachable | line 7078 predecessor .word       0x0000008B                   # movn        $zero, $zero, $zero # 00000080 <InstrIdType: CPU_SPECIAL> |
| funcs_37.c | `0x800CCA80` | movz $zero | 1 | post-return/unreachable | line 7129 predecessor mfhi        $zero |
| funcs_37.c | `0x800CCA88` | movn $zero, movn $zero | 2 | post-return/unreachable | line 7132 predecessor jr          $zero; line 7136 predecessor movn        $zero, $zero, $zero |
| funcs_37.c | `0x800CCF50` | movn $zero | 1 | data-like/unreachable | line 7751 predecessor lb          $t2, 0x6184($zero) |
| funcs_37.c | `0x800CD030` | movz $zero | 1 | data-like/unreachable | line 7865 predecessor .word       0x0020000F                   # sync # 00200000 <InstrIdType: CPU_SPECIAL> |
| funcs_37.c | `0x800CD034` | movz $zero | 1 | data-like/unreachable | line 7867 predecessor movz        $zero, $zero, $t9 |
| funcs_37.c | `0x800CD15C` | movn $zero | 1 | data-like/unreachable | line 8035 predecessor multu       $at, $s1 |
| funcs_37.c | `0x800CD160` | movn $zero | 1 | data-like/unreachable | line 8037 predecessor movn        $zero, $zero, $k0 |
| funcs_37.c | `0x800CD2D8` | movz $zero, movz $zero | 2 | data-like/unreachable | line 8246 predecessor bltz        $t0, L_800E2B60; line 8250 predecessor .word       0x0000014A                   # movz        $zero, $zero, $zero # 00000140 <InstrIdType: CPU_SPECIAL> |
| funcs_37.c | `0x800CD404` | movz $zero | 1 | data-like/unreachable | line 8431 predecessor nop |
| funcs_49.c | `0x800A2A2C` | movz $t7, movz $t7 | 2 | data-like/unreachable | line 9484 predecessor .word       0x00198E48                   # jr          $zero # 00198E40 <InstrIdType: CPU_SPECIAL>; line 9488 predecessor .word       0x001D7C4A                   # movz        $t7, $zero, $sp # 00000440 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2A6C` | movn $t5 | 1 | data-like/unreachable | line 9528 predecessor .word       0x001C1B49                   # jalr        $v1, $zero # 001C0340 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2AA8` | movz $sp, movz $sp | 2 | data-like/unreachable | line 9565 predecessor .word       0x001A2848                   # jr          $zero # 001A2840 <InstrIdType: CPU_SPECIAL>; line 9569 predecessor .word       0x001EEA4A                   # movz        $sp, $zero, $fp # 00000240 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2AE8` | movn $zero | 1 | data-like/unreachable | line 9610 predecessor .word       0x001CC649                   # jalr        $t8, $zero # 001C0640 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2B24` | movz $s4, movz $s4 | 2 | data-like/unreachable | line 9647 predecessor .word       0x0019E648                   # jr          $zero # 0019E640 <InstrIdType: CPU_SPECIAL>; line 9651 predecessor .word       0x001FA74A                   # movz        $s4, $zero, $ra # 00000740 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2B64` | movn $k0 | 1 | reachable | reachable guest predecessor; line 9696 after .word       0x001C7E49                   # jalr        $t7, $zero # 001C0640 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2BA0` | movz $t2 | 1 | data-like/unreachable | line 9734 predecessor .word       0x00186047                   # srav        $t4, $t8, $zero # 00000040 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2BE0` | movn $t7, movn $t7, movn $t7, movn $t7 (+1 copies) | 5 | data-like/unreachable | line 9771 predecessor .word       0x001ACF48                   # jr          $zero # 001ACF40 <InstrIdType: CPU_SPECIAL>; line 9784 predecessor .word       0x001ACF48                   # jr          $zero # 001ACF40 <InstrIdType: CPU_SPECIAL>; line 9794 predecessor .word       0x001ACF48                   # jr          $zero # 001ACF40 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2C50` | movz $s4 | 1 | data-like/unreachable | line 9882 predecessor sd          $zero, -0x33AE($fp) |
| funcs_49.c | `0x800A2C54` | movz $gp | 1 | data-like/unreachable | line 9884 predecessor .word       0x0004A24A                   # movz        $s4, $zero, $a0 # 00000240 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2C58` | movz $a1 | 1 | data-like/unreachable | line 9886 predecessor .word       0x000DE74A                   # movz        $gp, $zero, $t5 # 00000740 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2C5C` | movz $t6 | 1 | data-like/unreachable | line 9888 predecessor .word       0x00172C4A                   # movz        $a1, $zero, $s7 # 00000440 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2C90` | movn $v1 | 1 | data-like/unreachable | line 9922 predecessor sd          $k0, 0x7A53($sp) |
| funcs_49.c | `0x800A2C94` | movn $t1 | 1 | data-like/unreachable | line 9924 predecessor .word       0x0005194B                   # movn        $v1, $zero, $a1 # 00000140 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2C98` | movn $t7 | 1 | data-like/unreachable | line 9926 predecessor .word       0x000F4B4B                   # movn        $t1, $zero, $t7 # 00000340 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x800A2C9C` | movn $s6 | 1 | data-like/unreachable | line 9928 predecessor .word       0x00197E4B                   # movn        $t7, $zero, $t9 # 00000640 <InstrIdType: CPU_SPECIAL> |
| funcs_49.c | `0x801096F4` | movz $zero, movz $zero | 2 | reachable | reachable guest predecessor; line 11601 after sll         $zero, $s4, 0 |
| funcs_49.c | `0x8010A988` | movz $zero | 1 | data-like/unreachable | line 4768 predecessor .word       0x3F59999A                   # lui         $t9, 0x999A # 03400000 <InstrIdType: CPU_NORMAL> |
| funcs_49.c | `0x8010A9A4` | movz $zero | 1 | data-like/unreachable | line 4783 predecessor .word       0x3F59999A                   # lui         $t9, 0x999A # 03400000 <InstrIdType: CPU_NORMAL> |
| funcs_49.c | `0x8010A9C0` | movn $zero | 1 | data-like/unreachable | line 4798 predecessor .word       0x3F59999A                   # lui         $t9, 0x999A # 03400000 <InstrIdType: CPU_NORMAL> |
| funcs_49.c | `0x8010AB2C` | movn $zero | 1 | data-like/unreachable | line 4981 predecessor .word       0x3F59999A                   # lui         $t9, 0x999A # 03400000 <InstrIdType: CPU_NORMAL> |
| funcs_49.c | `0x8010AB48` | movn $zero | 1 | data-like/unreachable | line 4995 predecessor .word       0x3F59999A                   # lui         $t9, 0x999A # 03400000 <InstrIdType: CPU_NORMAL> |
| funcs_49.c | `0x8010AB64` | movn $zero | 1 | data-like/unreachable | line 5009 predecessor .word       0x3F59999A                   # lui         $t9, 0x999A # 03400000 <InstrIdType: CPU_NORMAL> |
| funcs_49.c | `0x8010AB80` | movn $zero | 1 | data-like/unreachable | line 5023 predecessor .word       0x3F59999A                   # lui         $t9, 0x999A # 03400000 <InstrIdType: CPU_NORMAL> |
| funcs_49.c | `0x8010AB9C` | movn $zero | 1 | data-like/unreachable | line 5037 predecessor .word       0x3F59999A                   # lui         $t9, 0x999A # 03400000 <InstrIdType: CPU_NORMAL> |
| funcs_49.c | `0x8010B0E8` | movz $zero | 1 | data-like/unreachable | line 5721 predecessor .word       0x3F6B851F                   # lui         $t3, 0x851F # 03600000 <InstrIdType: CPU_NORMAL> |
| funcs_49.c | `0x8010B13C` | movz $zero | 1 | data-like/unreachable | line 5764 predecessor .word       0x3F6B851F                   # lui         $t3, 0x851F # 03600000 <InstrIdType: CPU_NORMAL> |
| funcs_49.c | `0x8010B1D8` | movz $zero | 1 | post-return/unreachable | line 5848 predecessor sll         $t7, $t1, 0 |
