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
agrees with both; why the generated bodies ignore those sizes was not looked at.

`data_gap_` bodies stay in the lookup table even when their only direct site was in a cut tail. Dropping them needs proof
that no pointer reaches them, and the raw ROM scan cannot see inside compressed overlays.

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
