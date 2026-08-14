# s1094 retail loop PC-role audit

Static audit only. The generated function is `runIdleFramesAndLoadSaveData`
(`0x8006D900`, size `0x22C`). The raw ROM copy places that function at ROM
offset `0x6E500`, establishing `ROM = VRAM - 0x80000000 + 0xC00`.

| PC | ROM word | Generated instruction | Role |
|---|---:|---|---|
| `0x8006D980` | `0x0C000BFD` | `jal 0x80002FF4` | taken loop target / ordinary instruction |
| `0x8006D984` | `0x26100001` | `addiu $s0,$s0,1` | delay slot of `jal` |
| `0x8006D988` | `0x0C002A1B` | `jal 0x8000A86C` | ordinary sequential instruction |
| `0x8006D98C` | `0x00000000` | `nop` | delay slot of `jal` |
| `0x8006D990` | `0x0C0029B3` | `jal 0x8000A6CC` | ordinary sequential instruction |
| `0x8006D994` | `0x00000000` | `nop` | delay slot of `jal` |
| `0x8006D998` | `0x0C005B11` | `jal 0x80016C44` | ordinary sequential instruction |
| `0x8006D99C` | `0x27A40010` | `addiu $a0,$sp,0x10` | delay slot of `jal` |
| `0x8006D9A0` | `0x0C002DBD` | `jal 0x8000B6F4` | ordinary sequential instruction |
| `0x8006D9A4` | `0x00000000` | `nop` | delay slot of `jal` |
| `0x8006D9A8` | `0x0C00301F` | `jal 0x8000C07C` | ordinary sequential instruction |
| `0x8006D9AC` | `0x00000000` | `nop` | delay slot of `jal` |
| `0x8006D9B0` | `0x2E020020` | `sltiu $v0,$s0,0x20` | ordinary loop compare |
| `0x8006D9B4` | `0x1440FFF2` | `bne $v0,$zero,0x8006D980` | branch; target is `0x8006D980` |
| `0x8006D9B8` | `0x3C048014` | `lui $a0,0x8014` | delay slot of `bne` |
| `0x8006D9BC` | `0x2484A5C0` | `addiu $a0,$a0,-0x5A40` | ordinary fall-through instruction |

The generated comments in `scratch/agent/s389_verify/before_current_applied/funcs_17.c`
and the raw ROM words at `0x6E5B0..0x6E5EC` agree for every row. Therefore
the zero watch result for `0x8006D9B8` is explained by the pure-interpreter
debugger's delay-slot callback omission, but zero `0x8006D9BC` is not a
delay-slot omission. Whether the branch was taken on the observed execution
is a separate runtime question.
