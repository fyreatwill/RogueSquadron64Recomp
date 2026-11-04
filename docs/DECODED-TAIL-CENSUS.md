# Decoded data tails

Census from s6869, by `tools/fixup_cut_decoded_tails.py`. Static method, plus a machine code compare (below).

Some generated functions run past their real end into data that N64Recomp decoded as code. The tool walks each function
from its entry, then checks the C itself: no goto above the cut names a label below it, the cut is at brace depth 1, and
the last statement above it cannot fall through (`return`, `goto`, `do_break`, `__builtin_trap`). If all three hold, the
tail is dead code on every path, and that holds whether or not the body is real code. The step runs in
`tools/regen_replay.sh`, before the rename table.

`--self-test` injects a goto across the end and removes a `return` in memory on a real function; both must be flagged.

## Results

| Measure | Before | After |
|---|---|---|
| Functions cut | - | 18 |
| Refused | - | 2 (`data_gap_800CC3D4`, `data_gap_80024A0C`) |
| Generated lines | 1146851 | 1021478 |
| `funcs_*.c` size | 62 MB | 57 MB |
| Game binary | 38437080 bytes | 38354504 bytes |
| Compile funcs_27 / funcs_8 / funcs_49 | 4.71 / 2.22 / 1.35 s | 4.70 / 2.22 / 0.76 s |

Compile time barely moved. clang already dropped the tails after `return`: `audioCompandS16` and
`lvj_checkComplexObjectives` have the same machine code with and without them, which is a second, independent check that
those two tails were unreachable. The 16 functions that changed size stop at a `do_break`. That function exits but is not
declared noreturn, so clang kept the code after it.

Live before vs after: 2759 same, 24 differ, 0 missing. 16 of the 24 are cut functions. The other 8 keep their size and differ
only in addresses, adrp pages and string numbering; 2 of the 18 cuts show no difference (see above).

## What `.word` means

`.word` is not a code/data boundary. It marks words the disassembler disliked, and the generator still translated most of
them: of 8152 `.word` lines in the pristine tree, 3339 became `do_break`, and the rest are real statements that run on.
The walk stops only at a `.word` that became `do_break`. 951 `.word` lines remain in the live tree.

The two refusals have a goto above the cut, from a part of the body the walk did not reach (`bgez` at 0x800CC408, `bne` at
0x80024A30). They are left whole. Their bodies are `data_gap_` functions, so this costs about 7700 lines and nothing else.

`__OSGlobalIntMask` is a data object: its first word is `.word` -> `do_break`, so it now holds only that. The symbol has
size 0x4E10 in the toml. `audioCompandS16` (0x54) and `lvj_checkComplexObjectives` (0x8) have correct toml sizes, and the walk
agrees with both.

## Why the bodies ran long (s6870)

The size is lost in `make_elf.py`. It never reads `syms/rogue_squadron.syms.toml`; only `patches.toml` does. Symbols in
`symbol_files/*.txt` carry no size, so make_elf gives each function the distance to the next function symbol:

| Function | toml | ELF st_size | Generated words |
|---|---|---|---|
| `audioCompandS16` | 0x54 | 0x73B4 | 21 + 7384 tail |
| `lvj_checkComplexObjectives` | 0x8 | 0x2098 | 2 + 2084 tail |
| `mainGameLoop` (control) | 0x5BC | 0x5BC | agrees |

Across the ELF: 2519 functions agree with the toml, 111 differ, 0 are missing from it. N64Recomp honours what it is given.

`tools/regen_front.sh` feeds real sizes through N64Recomp's own `function_sizes` config, so no sibling repo changes. The table
is `tools/func_sizes.txt`, 6 functions, written by `fixup_cut_decoded_tails.py --sizes` from a tree before the cut. The other 12
of the 18 cuts are `static_` functions with no ELF symbol. They were only there because a jal in a decoded tail named them.

Effect: the cut step now reports 0 cut, 2 refused. Pristine output 957518 -> 832949 lines. 11 junk labels leave
`audioCompandS16`. 17 functions no longer exist: `data_gap_` 80029270, 80045024, 800A2114, 800A2218, 800A23BC, 800A2558, 800A2790,
800A2924, 800A29BC, 800A2B50, 800A2BE4, 800A2E98, 800A2F28, 800A2FE4, 800A50AC, 80106C50, 801096D8.

Dropping them removes them from the lookup table, so `tools/audit_ptr_reach.py` looked for pointers to them as data words and
as lui + addiu/ori pairs. It scanned every ELF section, a retail menu RDRAM image and two port mission images. Controls fired
(`runAiAudioStreamPlaybackLoop` in code, `mainGameLoop` in data). 16 of 17 have no hit. `801096D8` has code hits at 0x800AE428 and
0x800AE4EC: its words are 0x00140014 repeated, next to the u16 table D_80109710, so those look like table reads, not calls.
The scan cannot see a pointer built any other way, and the port images date from s5069.

Runtime: a lookup miss is fatal and prints `Failed to find function` (overlays.cpp `get_function`). Regen binary (`nm`: dropped
symbols absent, present in live), dd1 4:3, one run per level: lvl1 142 s and lvl5 143 s of flight, inits 1, alive, 0 stalls, 0
crash lines, 0 misses. No same-run control forces a miss. Other levels and menus beyond this route were not run.

The live tree is unchanged and still carries the 17 functions.

## Table (before the cut)

| File | Function | Entry | Real end | Lines | Tail words | .word in tail | do_break stops | Crossing | Fall-through | Hooks in tail |
|---|---|---|---|---|---|---|---|---|---|---|
| funcs_26.c | data_gap_80099FDC | 80099FDC | 8009A00C | 2489 | 981 | 241 | 1 | 0 | - | - |
| funcs_27.c | audioCompandS16 | 8009DD7C | 8009DDD0 | 103712 | 7384 | 2878 | 0 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity rs64_probe_submit_gate_store rs64_s5660_ustore s5660_a |
| funcs_37.c | data_gap_800CC3D4 | 800CC3D4 | 800CC528 | 2419 | 1022 | 333 | 2 | 1 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity rs64_probe_submit_gate_store |
| funcs_39.c | data_gap_800EC10C | 800EC10C | 800EC110 | 5 | 0 | 0 | 1 | 0 | - | - |
| funcs_4.c | data_gap_800186D8 | 800186D8 | 800186EC | 36 | 10 | 7 | 1 | 0 | - | - |
| funcs_40.c | data_gap_800EC6EC | 800EC6EC | 800EC6F0 | 5 | 0 | 0 | 1 | 0 | - | - |
| funcs_42.c | data_gap_800FBE14 | 800FBE14 | 800FBE18 | 9 | 2 | 2 | 1 | 0 | - | - |
| funcs_49.c | lvj_checkComplexObjectives | 80109638 | 80109640 | 4739 | 2084 | 730 | 0 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity rs64_probe_submit_gate_store rs64_s5660_ustore s5660_a |
| funcs_49.c | data_gap_800A2114 | 800A2114 | 800A21B0 | 197 | 26 | 8 | 1 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity |
| funcs_49.c | data_gap_800A2218 | 800A2218 | 800A222C | 315 | 100 | 47 | 1 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity |
| funcs_49.c | data_gap_800A23BC | 800A23BC | 800A23D4 | 315 | 97 | 30 | 1 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity |
| funcs_49.c | data_gap_800A2558 | 800A2558 | 800A256C | 431 | 137 | 20 | 1 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity |
| funcs_49.c | data_gap_800A2790 | 800A2790 | 800A2794 | 301 | 100 | 18 | 1 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity |
| funcs_49.c | data_gap_800A2924 | 800A2924 | 800A2964 | 122 | 22 | 5 | 1 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity |
| funcs_49.c | data_gap_800A29BC | 800A29BC | 800A29E8 | 336 | 90 | 33 | 1 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity |
| funcs_49.c | data_gap_800A2B50 | 800A2B50 | 800A2B64 | 154 | 32 | 15 | 1 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity |
| funcs_49.c | data_gap_800A2BE4 | 800A2BE4 | 800A2BEC | 546 | 171 | 78 | 1 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity |
| funcs_49.c | data_gap_800A2E98 | 800A2E98 | 800A2F14 | 107 | 5 | 5 | 1 | 0 | - | - |
| funcs_49.c | data_gap_800A2F28 | 800A2F28 | 800A2FD0 | 135 | 0 | 0 | 0 | 0 | - | - |
| funcs_49.c | data_gap_800A2FE4 | 800A2FE4 | 800A2FE8 | 615 | 122 | 70 | 1 | 0 | - | - |
| funcs_49.c | data_gap_800A50AC | 800A50AC | 800A50C8 | 159 | 22 | 5 | 1 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity rs64_probe_submit_gate_store |
| funcs_49.c | data_gap_801096D8 | 801096D8 | 80109710 | 31 | 0 | 0 | 0 | 0 | - | - |
| funcs_7.c | data_gap_80024A0C | 80024A0C | 80024B40 | 5244 | 1948 | 461 | 0 | 1 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity rs64_probe_submit_gate_store |
| funcs_8.c | __OSGlobalIntMask | 80039110 | 80039114 | 11375 | 4995 | 2074 | 1 | 0 | - | rs64_f5_store_shadow_post rs64_m5_writer_parity rs64_probe_submit_gate_store rs64_s5660_ustore s5660_a |

## Sizes past the first six (s6871)

`tools/audit_elf_tails.py` walks the ELF bytes rather than the generated C, pairs symbols by section (the overlays share
vram, and pairing by address alone gave wrong names), and lists what lands in each tail. Controls 80034010, 800371E0,
80037510 and 8002B600 all hit. Run with `--min 0x10`: 18 rows, the rest of the 111 are smaller padding.

| Function | Tail | Verdict | Action |
|---|---|---|---|
| audioCompandS16, lvj_checkComplexObjectives | 0x7360, 0x2090 | H-data | sized in s6870 |
| data_gap_80099FDC, data_gap_800186D8 | 0xF80, 0x34 | H-data | sized in s6870 |
| data_gap_80024A0C, data_gap_800CC3D4, fake_func_800AF6A8, rspbootTextPreamble | 0x1FA0, 0x1140, 0x1290, 0xD0 | H-data, entry has 0 references | sized |
| setRngSeed | 0x10 | H-data: the seed word itself sits at 80003470 | sized |
| osYieldThread | 0x1BB4 | H-data | none: not generated, the runtime replaces it |
| __osException | 0x3E4 | H-real: jump table at 8003A140 enters it, toml is short | none: not generated |
| tickCraftSelectScreen | 0xA9C | H-unnamed: handleCraftSelectInput, reached as a static | none |
| getTextureAttrBySlot, packMtxRowFloatToFixed | 0x164, 0x20 | H-unnamed: toml names a function, 0 references | none |
| resampleVoiceConstantSamples, resampleVoiceLutSamplesPacked | 0x84 each | H-unnamed: see below | none, must keep the tail |
| guMtxL2F, transformObjectColliderCenter | 0x64, 0x10 | pad | none |

The `jr ra` words in the data tails with no stack frames fit embedded RSP code, which keeps no frame. That reading is an
inference; the tails were not matched to a ucode. Walks from an entry nothing reaches are decoded data and prove nothing.

Effect: pristine 832949 -> 823108 lines. Cut step 0 cut, 0 refused. Compare 2684 same / 82 differ / 17 only live / 1 only
regen. The 4 new differences are exactly data_gap_80024A0C, data_gap_800AF6A8 (fake_func renamed), data_gap_800CC3D4 and
rspbootTextPreamble. Only regen: static_5_800CC4E4, which exists because the first data word of data_gap_800CC3D4 decodes as
a branch. Nothing enters it. Live funcs_50.c holds no functions, so the one-sided object loses nothing.

## Branches out of a function miscompile silently (s6871)

N64Recomp warns "branching outside of the function" (49 warnings in n64recomp.log, 36 after these sizes) and still emits
the goto. Labels print at the first pc >= their address, so a target below the function's entry lands on the entry and the
code compiles: the branch restarts the function. A target above it fails the compile, which is why forward cases carry a
hand-written `__builtin_trap` patch and backward ones were never noticed.

The real instances are 16 branches, 4 in each resampler helper (800927B0, 80092A54, 80092CF0, 80092F94). When a one-shot
sample ends ($s3 == 0) the helper leaves into the middle of its caller and never returns; the caller zero-fills and runs
its epilogue. Generated code restarts the helper instead, with $t1 rewound by the end pointer. The other warnings sit in
data_gap_ and fake_func_ decoded data, and applyVoiceDelayFilter's two are its last word, a toml data_gap.

**This code looks dead, so it is not fixed.** No jal, j, data word or lui pair reaches 8009264C..800934A4 from outside in
any section. Retail, 45 s boot + attract: 0 exec hits in that range while 80035500 and 80091B64 (audio) fired. Limits: the
range watch form had no same-run hit of its own, and two retail runs meant to reach a mission never hit tick 800FA730, so
missions are covered only by the static scan. A computed address would escape that scan.

A working fix was built and removed: the helper records the target and returns, the caller jumps to it after the jal. It
compiled and held lvl1 142 s, but its counters printed nothing at their 2^20 threshold, so that run says nothing about reach. If
any evidence of this block running turns up, reapply that design (PORTING-STATE s6871).
