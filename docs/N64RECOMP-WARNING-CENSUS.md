# N64Recomp warning census (s7082)

One fresh front-end pass (`tools/regen_front.sh scratch/s7082/regen`, real sizes from tools/func_sizes.txt; live tree
untouched). `n64recomp.log` has 247 lines, two classes, nothing else (0 jump-table, 0 unhandled-instruction, 0 error lines).

## Class 1: "branching outside of the function" — 56 warning lines, 36 distinct gotos (tools/scan_selfbranch.py)

| Rows | Where | Verdict | Owner |
|---|---|---|---|
| 16 | the 4 resampler helpers 800927B0 / 80092A54 / 80092CF0 / 80092F94 | H-live | fixed s7081, tools/fixup_selfbranch.py (differential test 2400/2400) |
| 2 | applyVoiceDelayFilter, word 0x8009D978/7C | H-data: after its `jr ra` at 0x8009D970; the word is the `$ra`-relative table its bltzal PIC idiom reads (s1971) | dead tail, toml data_gap |
| 2 | static_3_8009D978 (renamed data_gap_8009D978) | H-data: same table word decoded as a second entry | rename + DECODED-TAIL-CENSUS |
| 1 | rspbootTextPreamble 0x800825C8 | H-data, 0 references | sized 0x8 in func_sizes.txt (s6870) |
| 1 | fake_func_800B89F4 (renamed data_gap_800B89F4) | H-data | DECODED-TAIL-CENSUS |
| 14 | data_gap_8003DF98, _80040304, _80054648, _80099C4C, _800AEC54, _800BCC38, _800FEF04 (6), _80102A98, _80104208 | H-data | DECODED-TAIL-CENSUS (s6869-s6871) |

Matches the s6871 reading (49 warnings before sizes, 36 after); the only H-live rows are closed by s7081.

## Class 2: "No function found for jal target ... using runtime lookup" — 191 lines, 126 (caller, target) pairs

tools/s7082_jal_census.py classifies each target against every section's function table (recomp_overlays.inl):

| Lines | Class | Meaning |
|---|---|---|
| 188 | OTHER-SECTION-START | main-text caller, target is a function START in an overlay (mission / menu / cinematic share vram 0x800A5130). Runtime lookup resolves it against the loaded overlay. Correct lowering. |
| 1 | MID-FUNCTION | data_gap_800AF6A8 (cinematic, H-data, 0 references per DECODED-TAIL-CENSUS) -> 0x800EA01C, past the cinematic overlay's end |
| 2 | NO-FUNCTION | jal 0x8334B334 = the same applyVoiceDelayFilter table word as class 1 |

Overlay-dependent targets: 24 of the 66 distinct targets are a start in one overlay and mid-function in another, e.g.
0x800C58A0 (menuOverlayInit in menu, +0x320 into findClosestRadarContactAndSetSweep in mission, called from
mainGameLoop), 0x800AE878 (dispatchCinematicFromMainLoop), 0x800AE98C / 0x800AEA18 (cinematic getAssetNameForNpcType /
getCutsceneRuntimeContext, called from loadDatFile / parseDatItemSubtypes1To5). Retail bytes at each are `jr ra; <delay>`
of the previous function followed by a prologue, so they are real entries of that overlay, and the game picks the call by
which overlay it loaded. Every target is a function start in at least one overlay except the 3 H-data lines above.
A wrong-overlay call is not silent: get_function (lib/N64ModernRuntime/librecomp/src/overlays.cpp:644) prints
"Failed to find function at 0x..." and exits unless the missing-func stub env is set.

## Verdict

Every warning class has an owner: H-live only the 16 resampler exits (fixed s7081); everything else is decoded data or
correct overlay lowering. Positive control in the same pass: the 16 known resampler rows appear in class 1 and the
classifier finds overlay starts for 188/191 class-2 lines.

Not covered (no warning is printed for them): 81 `jr $reg` sites lowered to LOOKUP_FUNC tail calls and 177 jump-table
switches in the generated tree. That is the next silent-lowering census.

## s7083: the unwarned lowerings — `jr/jalr $reg` and jump tables (CLOSED, no miscompile)

tools/s7083_lowering_census.py over the same pristine front-end pass (scratch/s7082/regen) and the retail ROM:

| Class | Count | Verdict |
|---|---|---|
| `LOOKUP_FUNC(ctx->rN)` from `jalr` | 80 | indirect calls through function pointers (runtime lookup; a non-function target exits loudly in get_function) |
| `LOOKUP_FUNC(ctx->rN)` from `jr $non-ra` | 1 | convertMat3x4ToN64Mtx 0x80018E58 `jr $t9`, $t9 = $ra saved at entry (hand-asm return). Already patched to a host return by fixup_game_funcs_vendored.py (s2605); tools/check_jr_t9_host_return.py passes on the live tree |
| jump tables, all words match | 176 | table base recovered independently (lui/addiu chain into the addu before the jr), bound = nearest sltiu, words read from the ROM through the owning section's rom/ram map: count == bound, word[i] == case i label, every word inside the function |
| jump table, strength-reduced index | 1 | initHudStruct 0x800C14C4: index $s1 = 4*$s3 (loop-carried, seeded 0x20 / 8, both stepped together), bound on $s3 < 9; table 0x800A6560 matches 9/9 |

No missed jump table (the 81 "jr $reg" sites in NEXT.md were 80 jalr + 1 jr). Negative control, same pass: base+4 makes
177/177 tables MISMATCH.

Check (d), the dropped table load: N64Recomp lowers the `lw $r, 0(...)` feeding the jr to an ADD32 (address, not the
loaded code word), so $r is wrong at every case label. Safe only if no case path reads $r before writing it. DFS over
fall-through, taken and likely paths from all 1273 case targets (delay slots honoured, calls clobber caller-saved,
budget 600 insns): 0 reads; 754 write, 326 call, 193 exit. Controls: start at the jr itself -> READ 177/177; injected
control (first write on the path turned into `sw $r`) -> READ 692/692 (the other 62 writes sit in delay slots, not
injected). Before the delay-slot and call rules were added the scan reported 142 then 31 reads; every one inspected was
a `jal` return value or a delay-slot `lui` write, i.e. scanner defects, not code.

Verdict: N64Recomp's silent control-flow lowerings are correct for this ROM except the one jr-$t9 return, already fixed.
