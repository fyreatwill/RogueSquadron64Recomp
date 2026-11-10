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

## s7084: FPU lowering (CLOSED, no live miscompile)

Tools: `tools/s7084_fpu_census.py` (static, over scratch/s7082/regen) and `tools/s7084_fpu_test/run_test.py`
(host semantic test of the recomp.h FPU macros at the live -O2 flags). Both exit 0; rerun after any regen.

| Class | Count | Verdict |
|---|---|---|
| Lowering shape per op (43 op x fmt shapes, add/sub/mul/div/sqrt/abs/neg/mov .s/.d, cvt.*, trunc.w.*, ceil.w.d, c.lt/le/ole/eq, bc1t/f(l), l/s wc1/dc1, m/t fc1, c/t fc1) | ~59k sites | 0 unmatched. c.le/c.ole/c.lt/c.eq -> C `<=`/`<`/`==`: false on NaN in both. Negative control (one CVT_W_S mutated to TRUNC_W_S) is flagged. |
| cvt.w.s / cvt.w.d (rounding-mode sensitive) | 13 + 2 | 13 run at default RM=0 = host nearest-even (lrintf). Positive control: convertMat3x4ToN64Mtx's 3 are listed. The 2 cvt.w.d in guPerspectiveF run in the only ctc1 window (RM=1, toward zero). |
| ctc1 / set_cop1_cs -> fesetround | 3 (all guPerspectiveF, gcc's double->u16 perspNorm idiom) | Honoured: the built object has fesetround -> frintx/fcvtzs -> fegetround -> fesetround(restore), in that order. Host test: 144 rows (cvt.w.d/cvt.w.s/trunc.w.s/cvt.s.d in all 4 modes, value computed before the mode switch) match an exact MIPS reference; mode-blind negative control mismatches 33 rows. |
| cfc1 flag/cause reads (`& 0x78`) | 2 (guPerspectiveF) | **Differs, unreachable.** get_cop1_cs returns RM only, so flags read 0 and clang deletes the >=2^31 retry path. Retail reaches that path only if 131072/(near+far) >= 2^31, and the function already takes near+far <= 2 to the 65535 branch. |
| Odd-FPR direct access `ctx->fODD.*` | 750 in 10 asm math helpers | All 750 preceded by CHECK_FR, an assert that is live in this build (Debug, `___assert_rtn` in funcs_4.c.o), so an FR=0 execution aborts loudly and never miscompiles silently. Accesses through f_odd (mtc1/mfc1/lwc1 to odd regs, 127) map FR=0 to the even reg's upper half and FR=1 to the reg itself, as the R4300 does. |
| Status.FR toggles (mtc0 c0_sr) | 7 helpers set and clear FR; projectPointToScreen sets FR and never clears it | Retail bytes do the same (no static jal caller; jalr only). The runtime keeps FR per guest thread context, as libultra does (__osDispatchThread restores SR), so it matches hardware. |
| Likely branches bc1tl/bc1fl | 794 | All shaped `if (cond) { delay; goto L; } goto skip_N; <dead copy>`: delay slot runs only when taken. |
| FMA contraction (R4300 has no FMA) | 145 fmadd/fmsub in the built RecompiledFuncs | All 145 sit on injected patch C lines (host helpers: dist2, camera aim, dd/edge-fade math, probes), 0 on lowered guest statements. Pristine regen compiled with live flags: 0 fused (34 files that compile standalone), as fp-contract=on only fuses within one C expression and every guest op is its own statement. |
| FCSR.FS (flush denormal results) | retail FCSR 0x01000800 | Known difference since s6012: host FZ is off unless ROGUESQ_FTZ=1, so the port keeps denormal results that retail flushes to 0 (magnitudes < 1.2e-38). Left opt-in (s6013 soaks: no effect). |
| trunc.w.* / cvt.w.* out of range or NaN | n/a | Retail raises the unimplemented-operation exception (a crash); host saturates or gives 0. Lenient only on paths where retail would already have died. |

Verdict: no FPU lowering in this ROM differs from R4300 semantics on a reachable path. Next silent class: integer
mult/div and 64-bit lowering (hi/lo, div by zero, INT_MIN/-1, dmult/ddiv, lwl/lwr/swl/swr).

## s7085: integer lowering (CLOSED; one C-UB difference fixed in recomp.h)

tools/s7085_int_census.py over scratch/s7082/regen (output scratch/s7085/census.txt); host test
tools/s7085_int_test/run_test.py (int_test.c compiled at the live -O2 flags against an exact R4300 reference).

| item | sites | verdict |
|---|---|---|
| shapes (mult/multu/div/divu/ddivu, mflo/mfhi, sll/srl/sra/v, dsll/dsrl/dsra(32), slt/sltu/slti/sltiu, addu/addiu/add/subu, lwl/lwr/swl/swr) | 99,400 over 30 shapes | all match; 177 addu are the s7083 `jr_addend_` jump-table form. Negative control: one mult mutated S64(S32 -> U64(U32 is flagged (+1) |
| sltiu immediates | 876 sites, 83 distinct | none >= 0x8000, so the sign-extended-immediate edge case never occurs |
| mflo/mfhi with no mult/div earlier in the function (hi/lo are per-function locals) | 0 | none |
| div (90) / divu (45) zero / INT_MIN guards | 89 div guarded break7+break6, 43 divu break7 | retail traps on these; positive control 0x800464F4 (loadGridCellTilesByDistance) classified guarded |
| unguarded 32-bit divides | 3 | _Ldtob div by 100000, computeNoteRatePairFromTableA/B divu by 0x300: constant divisors, safe |
| unguarded 64-bit divides | 2 ddivu | u64DivU64 0x80007500 (divisor = 64-bit data at 0x80039100, callers computeElapsedMillis / emitProfilerBarSegment) and divideByMixerBaseFrequency 0x80093F2C (divisor *0x801440C0, set by resetMusyXEngineState). **Differed on /0: C UB, arm64 udiv gives lo=0; R4300 gives lo=-1, hi=a.** Fixed in recomp.h DDIV/DDIVU (hardware result for b==0) |
| add (overflow trap dropped) | 4, all bcopy_recomp | address + length on KSEG0 pointers; retail would fault, so only a crash path differs |
| do_break guards after a C division (could clang delete them as UB?) | - | host test: the generated 0x800464F4 shape with a variable divisor still calls do_break for /0 and INT_MIN/-1 at -O2. Object break counts drop only where the divisor is a constant (e.g. spawnNpcWithRandomRotation div by 45), where folding is correct |

Host test: 3476 rows (mult/multu/div/divu/dmult/dmultu/ddiv/ddivu over 17x17 values, every shift 0..63, sltiu/slti/ADD32/SUB32
with sign-extended immediates, lwl/lwr pairs and singles and swl/swr pairs and singles at all 4 misalignments, both guard shapes).
Before the fix: 34 mismatches, all divisor-0 ddiv/ddivu. After: 0. Negative control (zero-extending reference): 1436 mismatches.
Not covered: sra/srav on non-sign-extended inputs (architecturally undefined; lowering = ares's s32(rt.s64 >> sa)), single partial
lwr bits 63..32 (implementation-defined; low 32 compared).

## s7086: memory access, immediates and conditional branches (CLOSED, no live miscompile)

Tools: `tools/s7086_mem_branch_census.py` (offline, over scratch/s7082/regen + the live ../N64Recomp/RecompiledFuncs) and
`tools/s7086_mem_test/run_test.py` (host test at -O2 with the live flags). Unlike s7085, each site is checked with its
OPERANDS: register numbers and the immediate value printed in C must equal the disassembly's.

| class | sites | result |
|---|---|---|
| lb/lbu/lh/lhu/lw/lwu/ld | 383/5172/783/4894/26880/2/4 | all match; 177 lw are the jump-table loads s7083 proved are never read (177 = the s7083 table count) |
| sb/sh/sw/sd | 5321/4560/25554/46 | all match (SD high word at +0) |
| ll/sc/scd/sync | 0/0/2/0 | ll/sc/sync absent; the 2 scd are in decoded data (next unit) |
| cache | 37 | lowered to nothing (correct: no host cache) |
| lui/addiu/ori/andi/xori | 22262/34384/1904/6475/121 | values match; addiu lo16 sign-extended, ori/andi/xori zero-extended. 0 RELOC_ (main ELF is not relocatable), so %hi/%lo pairing has nothing to check |
| beq/bne/blez/bgtz/bltz/bgez | 7234/5969/351/127/107/241 | condition operator + operands match; delay slot inside the taken block then `goto L_target`, again on fall-through |
| beql/bnel/blezl/bgtzl/bltzl/bgezl | 747/878/13/9/33/32 | fall-through is `goto skip_N` past an identical delay-slot copy, so the slot runs only when taken |
| bgezal/bltzal + jal/jalr $ra reads | 8/6 | 6 sites read $ra after a link op before writing it: exactly the s1971 bltzal $zero PIC sites, all 6 patched in the live output |

Explained differences (182): 177 jump-table lw; 2 bgtz in interpolatePointTableSamplesToPackedWord /
interpolateLutSamplesToPackedWord where a stray out-of-function label (L_8009276C, L_80092A10) sits before the delay-slot
copy (the s7081 self-branch class; the live output dispatches through g_rs64_sbx_target, checked); 3 branches whose block
runs past the function end in decoded data (rspbootTextPreamble 0x800825CC, the 0x8009D97C table word twice). 8 more in
data_gap_/fake_func_. Labels on a delay-slot address: 4, all on the fall-through copy (correct).
Constant offsets misaligned for the width: 52 in real code (sh/sw in loadTopCloudsAsset, initializeRadar, loadSfxAsset,
updateCraftSelectAnimState, ...). They are the odd-base idiom: loadTopCloudsAsset sets `$s0 = $s3 + 0x26DF`, then
`sh -0x17($s0)` hits `$s3 + 0x26C8`, which is aligned. The macros XOR the summed address, so any split is correct when the
effective address is aligned; a misaligned one address-errors on retail.
Controls: positive ld 0x800934D4 and beql 0x8000354C enumerated and ok; s1971 6/6 found and patched. Negative: lbu ->
MEM_HU, one beql without `goto skip_`, one s1971 patch line removed: each adds exactly one finding.
Host test: 11522 rows (8 random fills x every aligned address in a 64-byte window x width 1/2/4/8 x 6 base/offset splits,
loads and stores against a big-endian byte model, plus lw/lwu sign/zero extension of 0x80000000): 0 bad. Negative control
(MEM_BU swizzle ^2): 3065 bad.

## s7087: residual opcodes and the coverage table (CLOSED; series CLOSED)

Tools: `tools/s7087_residual_census.py` (offline, over scratch/s7082/regen) and `tools/s7087_logic_test/run_test.py`
(host test at -O2 with the live flags). Output: scratch/s7087/census.txt.

| class | sites | result |
|---|---|---|
| and / or / xor | 889 / 1463 / 96 | operand-checked: `rD = S op T` with the disassembly's registers, full 64-bit, all match |
| nor | 44 | `~(S \| T)` on 64 bits (38 `~(0 \| T)`, the `not` idiom); all match. Sign-extended inputs give a sign-extended result |
| negu | 79 | `SUB32(0, T)`; all match |
| mfc0 / mtc0 Status | 9 / 13 | all in 7 hand-written FR=1 matrix routines (transformAndEmitFaceVertices, evalCubicSplineAtTime, mat3x4Multiply, transformVec3ByMat34, rotateVec3ByMat3x3, quaternionToMat3x4, projectPointToScreen): `mfc0; lui 0x400; or; mtc0` sets FR on entry, `nor; and; mtc0` clears it on exit. Lowered to cop0_status_read/write, which switch ctx->f_odd (FR=0: odd single = high half of fpr n-1; FR=1: own register) and assert on any non-FR bit. New contexts start FR=0 (recomp.cpp run_thread_function, value-init), matching the game's FR=0 o32 code |
| mfc0 Compare | 3 | data_gap_80099FDC (decoded data), do_break |
| mfc0 Count | 0 | the game's osGetCount (0x8002BF90) is replaced by librecomp `osGetCount_recomp` and has 0 call sites in the generated code. The shim zero-extended the u32; FIXED to `(int32_t)` (hardware sign-extends). osGetTime_recomp (14 call sites) already split the u64 into two sign-extended halves |
| .word | 7 | 6 in data_gap_ functions; 1 is `__OSGlobalIntMask` (0x80039110 = 0x003FFF01), a libultra data word the symbol file lists as a function, never called |
| scd | 2 (1 address) | 0x8009D8C0 after filterVoiceSampleBlock's `jr $ra`, under label L_8009D8BC; the only reference is `bltzal $zero, L_8009D8BC` (0x8009D7E0), the s1971 PIC idiom that is never taken: the bytes are a data table. Lowered to do_break, unreachable |

projectPointToScreen returns with FR still set (no clear on either `jr $ra`), retail too. It has no jal, no pointer word
in the ROM and no lui/addiu address build in the generated code, so it is dead; if it ever ran, the per-context f_odd
pointer would follow retail.

Other host shims writing $v0 (librecomp + src): every other `ctx->r2 = <u32>` returns a small value (AI length/frequency,
DP status, yielded flag, sizes) or an int32_t (handles at 0x80800000+, message results), so only osGetCount was affected.

Host test: 2176 rows (and/or/xor/nor over 17x17 values including non-sign-extended ones, nor/and/xor sign-extension
preservation, negu, f_odd aliasing for all 16 odd FPRs in FR=0 and FR=1 on the real recomp_context, osGetCount extension):
0 bad. Negative control (nor as `(S|T)`, negu as ADD32): 303 bad. Census controls: positive `and` 0x80004910 and Status
read 0x800196A8 enumerated and ok; negative: one nor and one negu mutated, exactly 2 new findings.

**Coverage: 120 mnemonics, 326,200 sites, 0 unmapped.** Every mnemonic in the front-end output is named by at least one
census tool: s7083 control flow (j/jal/jr/jalr/b*, break, cache, jump tables), s7084 FPU (all .s/.d ops, c.*, bc1*,
lwc1/swc1/ldc1/sdc1, mfc1/mtc1, cfc1/ctc1), s7085 integer (mult/div family, shifts, slt*, addu/subu/add/daddi,
lwl/lwr/swl/swr), s7086 memory/immediates/branches (all loads/stores, lui/addiu/ori/andi/xori, every conditional
branch and likely form), s7087 and/or/xor/nor/negu, mfc0/mtc0, .word, scd, nop. The mapping is checked by name mention
in each tool's source (tools/s7087_residual_census.py `coverage`). **The N64Recomp lowering series s7082-s7087 is
closed: no live miscompile remains; the two semantic gaps found (ddiv/ddivu by zero, s7085; osGetCount zero-extension,
s7087, dead here) are fixed.**

## s7088 host-shim ABI census (one layer up: the hand-written `*_recomp` shims)

Tool `tools/s7088_shim_abi_census.py` (controls built in), host test `tools/s7088_shim_test/run_test.py`.
129 shims (librecomp/src + src/, no duplicate definitions), **55 called** from generated code (286 call sites),
73 uncalled. Checks per body: A 64-bit arg joins (hi = even reg r4/r6, lo = hi+1, low word masked), B stack args
(sp+0x10.., u64 8-aligned), C integer returns sign-extended, D `_arg`/`_return` limits. Controls: pre-s7087
osGetCount body flags C (positive), osGetTime clean, osSetTimer with r6/r7 swapped gives exactly +1 A (negative).
**Verdicts: 52 match, 3 differs-unreachable, 0 differs-live.** The 3: osVirtualToPhysical (returns <2^29 for all 7
task-pointer callers), osAiSetFrequency (<= 368,800 or -1), osSpTaskYielded (0/1): zero- equals sign-extension.
Uncalled osAiGetLength also returns a bare u32 (dead).
Semantic gap found beyond the ABI: **osAiSetFrequency used integer rounding `(clock + f/2)/f`; the ROM (0x80029D20)
uses single-float `clock/(float)f + 0.5f` truncated, and returns -1 when dacRate < 132.** They disagree on 22 inputs in
1..400000 (none of 8000/11025/16000/22050/32000/44100/48000). FIXED (ai.cpp `rs64_ai_set_frequency_retail`, s7088
markers): host test shim == ROM transcription on 400,000/400,000; the game passes 22050 and gets 22047 either way
(live boot, 45 s, audio queue live), so the fix changes no observed value here. 64-bit shapes (__ll_mul, __ull_div,
__ull_rem, __ll_div, osSetTimer countdown join, osGetTime split): 1889/1889 on operands with bit 31 set in either
half; negative control (low-word masks removed) 323 mismatches. Not covered: non-ABI semantics of the remaining
called shims (what each returns vs the libultra routine it replaces) — that is the next unit.

## s7089 host-shim RESULT census (which shim results the game reads, and do they match the ROM)

Tool: `tools/s7089_shim_result_census.py` (offline; exit 0 = controls pass, count exact, 0 duplicate calls).
Forward liveness walk over the retail ELF (all code sections) from every `jal` to a called shim that the
generated tree contains: a $v0/$v1 read before a write = consumed; `jr ra` with the register live = handed to the
containing function's callers (followed, depth <= 4); a call kills both; delay slots and branch-likely
nullification honoured. 142 ELF jal sites sit inside libultra routines that are themselves replaced by shims and
are dropped. Controls: 0x80003874 osRecvMesg -> `beq v0,v1` must be consumed (PASS); synthetic overwrite unread
(PASS); synthetic `jr ra` returned (PASS); ELF sites in generated code 285 == generated shim calls 285 (PASS); a
per-function duplicate-jal detector reports 0 (PASS). Run on the pre-fix funcs_24.c the same tool reports 286 vs
285 MISMATCH and 2 duplicates (positive control for the defect below).

Result: 31 of the 55 called shims have results nobody reads. The 24 consumed ones against the ROM routine:

| shim | consumer reads | shim value | ROM value | verdict |
|---|---|---|---|---|
| __ll_div/__ll_mul/__ull_div/__ull_rem | v0:v1 (_Litob, printf path) | 64-bit split, sign-extended halves | same | matches (divisor is the radix, never 0) |
| __osDisableInt | v0 -> a0 of __osRestoreInt (0x80091274, musyxSynthFrame) | v0 unchanged | old Status IE | matches in effect: the only reader is the paired no-op __osRestoreInt |
| osAiSetFrequency | v0 stored to 0x801496F4 (2 sites) | ROM float formula (s7088) | same | matches |
| osEepromProbe | v0 != 0 | 1 (Eep4k) | 1 for a 4K EEPROM | matches |
| osEepromLongRead/Write | v0 == 0 / error path | 0 | 0 on a present EEPROM | matches |
| osMotorInit/Start/Stop | v0 == 0 | NOPACK/CONTRFAIL/DEVICE/0; INVALID when uninitialised | same codes | matches |
| osPfsInitPak/AllocateFile/DeleteFile/FindFile/ReadWriteFile | v0 == 0 | 1 = PFS_ERR_NOPACK | 1 with no pak | matches (no Controller Pak on the host) |
| osGetTime | v1 (low word), 14 sites | u64 split (s7088) | same | matches |
| osRecvMesg | v0 == -1 / bltz (5 of 53 sites) | -1 empty+NOBLOCK, else 0 | same | matches |
| osSendMesg | v0 == -1 (0x80007000) and factor5MutexRelease's return | -1 full+NOBLOCK, else 0 | same | matches |
| osSpTaskYielded | v0 < 2 loop (0x80019E14) | 0 (completion-wins model) | SP_STATUS_YIELDED bit | matches the no-yield model; the ROM's task-flags write needs SP YIELD status, never set here |
| osStartThread/osStopThread | v1 only through 4-deep void return chains (depth cap) | - | void | not a real consumer (compiled C never reads v1 after a void callee) |
| osVirtualToPhysical | v0 stored into task fields (7 sites) | K0/K1 & 0x1FFFFFFF | same | matches (s7088) |

**Defect found by the count control (FIXED): reapplyAudioConfig (retail 0x80091C88) ran initFactor5Mutex and
osAiSetFrequency twice.** Writer: the s3531 selector-setup-contract block in tools/fixup_game_funcs_vendored.py
replaced needles with `call + needle if "jal" in needle`; the two multi-line needles contain "jal" and their
replacement already contains the whole block, so the block was pasted twice (the first mutex copy without its
`goto after_0`). Retail executes each once. Effect: osCreateMesgQueue(0x80149990,1)+osSendMesg twice per call;
a thread woken by the first send would hold the token while the second send hands out another (two holders of
the Factor 5 mutex). Fix: the rule now prepends only for one-line needles (checked on the pristine s7082 pass:
1 call each, block equal to live modulo the later s4307 layer), and tools/fixup_s7089_dupcall.py (idempotent,
in the vendored chain) removed the second copies from the live tree. Built binary: one `bl` to each in
_reapplyAudioConfig.

## s7090 fixup-layer statement census (does any fixup repeat or lose a retail statement?)

Tool: `tools/s7090_fixup_statement_census.py` (offline, ~3 s; exit 0 = no untagged dup/drop/foreign).
Pristine = scratch/s7082/regen (front-end N64Recomp pass, no fixups). Live = ../N64Recomp/RecompiledFuncs.
Functions are matched by first guest address (renames ignored). Statements are filed under the preceding `// 0xADDR:`
comment; `{ X; RS64_S5798_ST(..); }` / s4307 synth-read wrappers are unwrapped, `rs64_*`/`RS64_*`/`rsNNNN_*`/
`g_rs64*`/fprintf/declaration statements and `if (__builtin_expect(g_rs64...))` lines are dropped, `name(rdram, ctx);`
becomes `CALL(rdram, ctx);`. A line carrying `PATCH` or a `// sNNNN` / `/* sNNNN` comment is tagged, and so is every
line until the braces it opens close.

| class | count | meaning |
|---|---|---|
| identical functions | 2,050 / 2,476 | statement multisets equal at every address |
| patched | 14,311 | difference carried by tagged lines (of which 186 shortfalls: see tools/s7090_shortfall_classify.py) |
| added | 197 | untagged code N64Recomp never emits in that function (PATCH-block bodies the brace rule misses) |
| moved | 20 (10 pairs) | an s803 VI probe swallowed the `// 0x` comment, so the call is filed one address earlier |
| unref-label | 18 | a label no goto in the function targets (e.g. renderVoiceAudioBlock's stray L_8009D980) |
| dup / dropped / foreign | **0 / 0 / 0** | |
| extent mismatch (not compared) | 3 | data_gap_80024A0C, data_gap_800CC3D4, rspbootTextPreamble: sized differently by the two passes |

Positive control: `--file-override funcs_24.c=scratch/s7089/funcs_24.pre.c.gz` gives dup=3 (reapplyAudioConfig 0x80091CB0
ADD32 + initFactor5Mutex, 0x80091CBC osAiSetFrequency), exit 1. Negative control: 2,050 identical functions.
Tagged excesses of a retail statement at its own address: 5, all null-pointer guards that `goto` the retail branch target
(reserveAndEmitDLEntry s169, submitSceneNodeRender s3553). Shortfall classes: rewritten-same-lhs 93, other-stmt-at-addr 46,
control-replaced 35, addr-block-absent 16 (s327 audio wait-spin pump), bare-drop 9 (dead copies after `return;` cut by
s6869, `$zero` writes, the moved VI calls). Not covered: build/factor5_ucode.

## s7093 RSPRecomp scalar-unit lowering (tools/s7093_su_census.py --controls, exit 0)

Pristine pass of the 3 compiled RSP TUs, ROM-decoded by the tool's own decoder. A decode 1,777/1,777 records match;
B control flow + delay slots 0 defects (main 0x1FF0 bgez wrap to IMEM 0x000 = goto L_0000, owned by the "L_0000
self-restart" fixup); C cop0/cop2 forms all match; D 1,083 live distinct scalar lines 94,060 cases 0 bad, 1,090
RSPRecomp-generated synthetic boundary lines 91,360 cases 0 bad; E MFC2/MTC2/CFC2/CTC2 3,473,408 cases 0 bad vs cxd4;
F jal link bit 12 (0x1xxx vs hardware 0x0xxx): all 11 non-jr $31 readers are save/restore -> jr, harmless.
Defect fixed: `sltiu rt, $zero, <negative imm>` emitted `0 < -0X...` (signed int compare); now `0 < U32(-0X...)`
(RSPRecomp commit 85c6156; 0 live sites, ucode regen 12/12 byte-identical). Rerun after any RSPRecomp change.
