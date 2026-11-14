# Fixed-address tests on guest pointers (s6862 audit)

Class: a host patch compares a guest pointer with a literal, so its behaviour depends on where the heap lands. The s6860
lvl10 HUD bug is the model (`elem < 0x80300000` on a heap table). Main heap is 0x80154690..0x8071B670 at 8 MB, and it extends
with OSMEM; spill is 0x80800000 or 0x81000000. Re-run with `tools/audit_heap_addr_tests.py` (exit 1 = unreviewed hit).

Method limit: static reading, single-source. The tool's review list is by function prefix (`rs64_s`, `rs5`, `rs6`, ...), so a new
behaviour-changing bound inside one of those prefixes is not flagged; read new patches by hand.

| Idiom | Live sites | Verdict |
|---|---|---|
| Pointer guards `>= RS64_RAM_TOP` | 1010 generated | Correct: follows the layout (top = OSMEM, or RAMTOP_MB 16/20, which covers the spill arena) |
| `< 0x81000000` heap walks, DL chunk walks (s6285, partitionFramebufferMemory, mainBootstrapWorker) | ~455 | Correct by design: the heap and DL pool stay under the RSP-visible 16 MB; spill blocks are not on those chains |
| `0x80300000..0x80330000` NPC def (s5810-s5835 family) | 13 | Heap-dependent, harness only (LOG_HITS, LOG_HUDBIT, NPC_INVULN). Can read as a false zero on another level |
| `(x >> 24) == 0x80` | 44 | Harness/logging, except a dump in osSpTaskStartGo. Rejects 0x81 spill pointers: false zero risk only |
| `<= 0x803FFFFF`, `< 0x80400000` | ~22 | Diagnostic values in log lines (s2173, s2179, s4279, s5798) |
| `0x807FFFxx`, `< 0x80800000` in src, rt64, s4204-s4208, s6657 | ~100 | Diagnostic or parked G1(d) harness; above 8 MB they log less, nothing else changes |
| `& 0x7FFFFF`, `& 0x7FFFFC`, `< 0x800000` physical | ~205 | Diagnostic: dumps, probes, env-gated DL walkers. Would fold >8 MB addresses in a log, not in rendering or audio |
| `origin == 0x790400 / 0x6AB400 / 0x696100 ...` | ~400 | Log phase gates only; they stay silent when wide layouts move the framebuffer |
| Static-object bounds (0x80130DB0 span table, 0x80138060.., 0x801107E0, 0x80128EA8) | ~30 | Static data, fine |
| s4563 `fp == 0x80179380` + `head in 0x80179380..0x8017970C` | 1 | Heap literal, default ON, but DEAD: removed s6865, see below |
| FS slot 0x76DF60 | 4 | Heap literal, opt-in only (LOG_FS_SLOT, FS_PIPE_INJECT default off) |

## s4563 stale-head skip is dead

Removed s6865: gone from the live tree and the replay list, ROGUESQ_S4563_SKIP no longer exists.

The check survives in musyxSynthFrame but its setter does not: `g_s4563_blk_freed` is only ever read. The setter sat inside the
`s4561 order` block in rs_free, anchored on the `s4300 rsfree bt` log line, and neither marker is in the live funcs_0.c. Even
when present it needed ROGUESQ_LOG_RS_FREE (s4565). The hazard is covered by s4786 PAUSE=4 (default on), which holds synth from
teardown to audio re-init by hook position, so it does not depend on the heap address.

## Replayed patches missing from the live tree

`tools/audit_heap_addr_tests.py` lists 9 replayed scripts whose MARK is absent (s2463, s4221-3, s4300, s4466, s4560, s4602, s4680).
s6863 answered why: they are removed on purpose after the fixer. Staged replay, with the s4296 A14 marker present at every stage as control:
`strip_diag_layers.py` removes 7, `fixup_live_replay.py` removes s2463 and s4221. The list is expected, not a defect. The s4563 setter goes the same way.
`tools/audit_replay_survival.py` covers the scripts without a MARK.

## Runtime check (21:9 + FPS60 + dd4, spill at 0x81000000, ROGUESQ_HUD_LOG=1, same binary)

| Level | vp 0x80138D20 elements | Heap HUD table | Reticle (static) | [s4562] pause set | [s4563] lines |
|---|---|---|---|---|---|
| 1 (control) | 10 | 0x805622CC..0x8056241C | 0x8010CA58/88 | 6 | 0 |
| 10 (control) | 10 | 0x8028FD3C..0x8028FE8C | 0x8010CA58/88 | 7 | 0 |
| 5 (264 s hold) | 10 | 0x8055D2FC..0x8055D44C | 0x8010CA58/88 | 7 | 0 |
| 14 | 20 | 0x8055BB5C..0x8055BF04 | 0x8010CA58/88 | 6 | 0 |

The table moves by level and always stays above the 0x80110000 bound; heap starts at 0x80154690, so it cannot fall below it.
A 131 s lvl5 hold logged 0 elements (still in its cinematic), so that arm was discarded and re-run. All arms alive, 0 stalls, 0 crash lines.

## Retail-side RAM-size and upper-bound constants (s7315)

The tables above read host-patch C literals. Retail MIPS builds its bounds in registers (`lui`+`ori`, then `sltu`), so those
sites never show up as C literals; s6992's 0xFF000000 pointer-mask class was the first one found this way. `tools/s7315_retail_bound_census.py`
reads the original-instruction comments in RecompiledFuncs and lists every `lui` of a RAM-size high half (0x003F/0x0040/0x007F/
0x0080/0x00FF) or a KSEG0 top (0x8040..0x8100), plus every osMemSize (0x80000318) load. It names the consumer and checks a verdict
table (exit 1 = unclassified; `--selftest` runs a fake `lui 0x8080; sltu` + osMemSize function, which must come back unclassified).
Run 2026-11-14: 86 distinct PCs (84 lui + 2 lw, the same count as an independent grep), 0 unclassified.

| Site | Verdict |
|---|---|
| partitionFramebufferMemory 0x80000EB4/0x80000EBC | Framebuffer top = 0x80400000 in 4 MB mode, else 0x80000000\|osMemSize. Follows OSMEM_MB, no fixed heap bound |
| getUsableRdramSize 0x80002664 | Returns 4 MB when the mode flag (*0x8010FCB0+0x44 & 0x2000) is set, else osMemSize |
| resetGameSettingsAndMissionStats 0x8006E5CC, initIdleDemoTimersAndSave 0x8006ED1C | settings 0x80130B63 = (usable > 4 MB). Expansion-pak flag, 1 at both 8 and 12 MB |
| applyRgbaTintToMeshVertices, buildAndRegisterDefaultMaterial | 0x80808081 = divide-by-255 magic |
| 70 others | Flag bits (or/and), MusyX 16.16 volume/pitch values (0x7F0000, 0x3F0000, 0x800000, 0x400000), 0x00FFFFFF/0xFF0000 field masks |

Result: retail code has no fixed heap upper bound built from a constant, and nothing that branches on 8 MB vs more. The only
size-dependent code is the 4 MB-vs-more split. So raising osMemSize (OSMEM_MB=12) changes the framebuffer placement and nothing else in
retail code. Method limit (single-source, static): a bound loaded from a data word or derived from a heap-end variable is not caught.
The s6992 mask class, the s6862 host-literal table and the dd>1 300 s holds at OSMEM_MB=12 are the dynamic side of that.

## Retail pointer tests against DATA-word bounds (s7316)

Complements s7315 (lui-built constants only). `tools/s7316_data_bound_census.py --ram <dumps>` lists every retail
`slt`/`sltu` whose one operand was loaded with `lw` from a constant global address G and whose other operand is not a constant,
then reads each G in ROGUESQ_RDRAM_DUMP_DIR dumps. Run s7316: L1 16:9 dd2 (OSMEM 12, spill 0x81000000 live, 216 spill blocks
all at 0x81xxxxxx, max request 0x8000), 29 dumps from boot to 137 s of flight.

| G | Sites | Runtime value | Verdict |
|---|---|---|---|
| 0x801163D4 DL pool limit | 169 | 0x80917B28..0x80B66720 | DL write pointer vs limit of the same pool; pool carved from the main heap at init, under 16 MB, never spill-served |
| 0x8011DC58 DL chunk pointer | 43 | same range | same pool |
| 0x801163B0 RDP-init DL pointer | 1 | same range | same pool |
| 0x8010FF18 heap head block | 2 | 0x80154690 | free-list walk in initMainHeap/coalesceFreeHeapBlocks; spill blocks never join the chain (rs_free hook returns on rs64_s6569_isspill first) |
| 37 other globals | 88 | scalar in all 29 dumps | counts, sizes, ids, timers (audio sorted tables, terrain grid dims, pool phases) |

The stored heap bounds 0x8010FF08..0x8010FF14 (written by initMainHeap/coalesceFreeHeapBlocks) have no retail `lw` reader
at all. No G held a spill pointer in any dump, while 80-87 heap words did (scratch/s7316/spill_words.txt), so the dump read
sees spill pointers where they live. Control: the same census on a dump with 0x81000040 written at 0x801163D4 flags all 169
sites. Verdict H-clean: no retail data-word bound rejects or misorders a spill pointer. Method limit: linear pass without a
CFG; a G read through a register base (struct field) is not followed; a G that holds a pointer only outside the dumped
phases is classed scalar. Single run, static + runtime lines agree.

## Spill-pointer holders and the struct-field edge (s7317)

Instrument: `ROGUESQ_S7317_ALLOCMAP=1` + `ROGUESQ_RDRAM_DUMP_BYTES=20971520` beside `ROGUESQ_RDRAM_DUMP_DIR` writes `alloc_<swap>.txt`
(every live heap and spill block, host caller names; guest ra is 0 in rs_malloc). `tools/s7317_spill_holders.py <dir>` classes each
spill-range word (live_ptr / dangling / data) with owner block, offset and caller; `--selftest` plants a pointer.
- dd2 16:9 L1: spill is load-window-only (833 recorded, 833 freed before swap 600), 0 live spill blocks in flight.
- dd8 21:9 L4: 22-120 live spill blocks in flight, up to 2747 holder words, 42 owner types (scratch/s7317/d8_owner_table.txt).
`tools/s7317_field_compare_census.py <holders_all.txt>`:
- Class A, top-byte shift then compare (shift form of the s6993 mask test): 32 sites, all spill-equal by evaluation. CLOSED.
- Class B, field-vs-register ordering compares at holder offsets: 182 sites, CLOSED s7319 (below).
- Class C, field pointer differences (`subu/sub d, p, q`, one operand a holder-field load, other non-constant): 155 sites, CLOSED s7320 (below).
- Class D, 24-bit truncation (`and` with a mask lacking bit 24 but keeping bits 16-21, or `sll k + srl k`, k >= 8): 26 sites whole-program, CLOSED s7321 (below).
s7316 global-word census re-run on the dd8 dumps (2113 static words holding live spill pointers): 0 spill-valued sites.

## Class B field-order compares closed (s7318 runtime + s7319 static)

Runtime (s7318, ROGUESQ_S7318_BCMP, 4 runs: dd8 21:9 L4 x2, L1, L12): 119/182 sites executed, 21.2M compares, **0 cross**
(spill vs 0x80xxxxxx), controls 3968/3968 classed cross. The only spill-operand compares are 8 zlib window sites (one block, H-same).
Static (s7319, `tools/s7319_bcmp_static_class.py <tables>`): the 63 never-executed sites, each class signature re-checked against
the generated MIPS (accepts all own sites, rejects >=40 foreign sites; dropping 3 tables makes coverage FAIL = control).

| class | kind | sites | meaning of the compared field |
|---|---|---|---|
| heap-size | scalar | 0, 8 | rs-heap block size vs request / running max |
| heap-freelist | same | 2 | block header vs neighbour header in one rs-heap freelist (spill arena is its own allocator) |
| asset-length | scalar | 6, 7 | asset load offset/length (0x20, 0x60) vs remaining length |
| frame-counter | scalar | 19, 20 | global frame stamp 0x8013889C vs per-object stamp 0x3C |
| halfword | scalar | 29 | lhu value (data_gap disassembly) |
| ctr-table | scalar | 17 sites (32 ... 123) | signed objective counter table 0x80138060[id-1] vs threshold field |
| loop-count | scalar | 34, 40, 41 | loop index vs element count field |
| blob-offset | scalar | 36-39 | file-relative offsets (4-aligned check) vs blob size, before relocation |
| voice-handle | scalar | 50, 51, 53, 57-59 | MusyX voice handle id vs sorted list node id (0x8) |
| voice-pitch | scalar | 52 | glide pitch current vs target (shifted by 8) |
| sched-time | scalar | 87 | signed message time vs field 0x1C4 |
| float-trunc | scalar | 116 | trunc.w.s value vs field 0x34 |
| tlut-pool | same | 127 | TLUT table entries vs freed entry, all inside one pool (compaction shift) |
| inflate-window | same | 131-133, 156 | zlib window/read/write/end (0x24-0x30) of one inflate state |
| inflate-avail | scalar | 134 | avail_in count min |
| huft-count | scalar | 158, 159 | Huffman code counts |
| pfs-page | scalar | 163-168 | controller-pak page numbers (signed) |
| printf-prec | scalar | 170-177 | _Genld precision/width |

Verdict: 57 scalar + 6 same + 119 runtime-clean = 182/182, **0 H-cross**: no class-B compare can order a spill pointer against
another allocation. Static half is single-source (one reader + mechanical signature), the runtime half is independent.

## Class C field pointer differences closed (s7320 runtime + static)

Census: `tools/s7317_field_compare_census.py <holders_all.txt>` class C (selftest plants a cross-base field difference, must list it
with its sltiu consumer, and must NOT list a constant subtrahend): 155 sites, 152 unique pcs (3 shared by the data_gap_80029270 /
huft_build_recomp duplicate-VA copies), table tools/s7320_bdiff_sites.txt (idx 256+i).
Runtime (s7320, `tools/apply_s7320_bdiff_probe.py` hooks into the s7318 classifier, table now 512 slots; report
`tools/s7320_bdiff_report.py`): dd8 21:9 L4 FPS60 WIDEWIN, 246 s flight, alive, 0 crash, 0 VI stall. 98/155 sites, 2.33M
subtractions, **0 cross** (spill minus 0x80xxxxxx or reverse), control at inflate_flush 0x80029B70 1398/1398 classed cross.
Every spill-operand subtraction is zlib: same-block (18787) or both-spill with one operand one-past-the-end of the window block
(spsp 250 / unm 485: `end - q`, end = window + size is outside [start, start+req) by construction), or spill pointer minus a scalar
distance/length (speq 18442: `q - dist`, `end - e`, the result is a pointer into the same window).
Static (`tools/s7320_bdiff_static_class.py <tables>`, signatures re-checked on the generated MIPS, each rejects >=40 foreign sites;
no table -> COVERAGE FAIL = control): the 57 never-executed sites.

| class | kind | sites | meaning |
|---|---|---|---|
| heap-freelist | same | 258 | split block minus its header inside one rs-heap block |
| heap-size | scalar | 268 | block size minus request |
| asset-pos | scalar | 263, 264 | asset load position 0x60/0x68 (zeroed at init) vs entry length 0x1C / stream position 0x24 |
| mul-idiom | scalar | 17 (270, 271, 280, 284, 286, 308-317, 319, 325) | `x<<k - x` strength-reduced multiply of an index, then scaled again |
| health-timer | scalar | 278, 279, 329, 330, 334-336 | NPC health / timer minus lhu damage step, max minus current |
| musyx-samples | scalar | 294, 295, 298 | MusyX voice sample positions 0x38/0x3C/0x40 vs truncated cursor |
| cp0-timer | scalar | 342, 343 | CP0 Count/Compare deltas (exception/timer code) |
| inflate-window | same | 347-352, 370, 374, 376, 378-380 | zlib window/read/write/end (0x24-0x30) of one inflate state |
| inflate-avail | scalar | 353 | avail_in -= n |
| inflate-input | same | 344 | next_in after minus before (total_in update) |
| huft-count | scalar | 391-393 | Huffman counts / code values |
| printf-prec | scalar | 400-406 | _Genld width/precision fields |

Verdict: 43 scalar + 14 same + 98 runtime-clean = 155/155, **0 H-cross**. With classes A, B and C the holder-field edge of the
spill-pointer class (order, top byte, difference) is closed. Static half single-source; runtime half independent.

## Class D 24-bit truncation closed (s7321 runtime + static)

Spill 0x81xxxxxx & 0x00FFFFFF drops bit 24: the masked value aliases low RDRAM, or aliases heap if re-tagged with | 0x80000000.
Census: class D in `tools/s7317_field_compare_census.py`, whole program (any non-constant source, holder-field loads marked). Kept-bit
mask M lacks bit 24 and keeps bits 16-21. Single-bit flag tests such as 0x10000 are excluded; the first, looser criterion listed 135.
Selftest: field & 0x00FFFFFF and sll8/srl8 are listed, & 0x1FFFFFFF and sll3/srl3 are not. Result: 26 sites (13 from holder fields).
Table: tools/s7321_trunc_sites.txt (idx 512+i).
Runtime: `tools/apply_s7321_trunc_probe.py` feeds each source with 0x80000000 into the s7318 classifier (table 768 slots; 512+ =
class D; cross = source in spill). Report: `tools/s7321_trunc_report.py`. Run: dd8 21:9 L4, FPS60 WIDEWIN, 250 s flight, alive, 0 crash,
0 VI stall. 19/26 sites executed, 66.3M truncations, **0 spill sources**. Control ROGUESQ_S7318_BCMP_CTL=800173C0 classed
9313/9313 as cross (PASS). A first run with ctl on 0x80008624 got ctl_n=0: that site never ran while a spill block was live.
Tables: scratch/s7321/bcmp_l4b.txt and bcmp_l4.txt.

Latent hazard, a real alias shape that is not reached: `commitMeshDrawBatchRefs` (0x80008624) rebuilds `a0 = (ref & 0xFFFFFF) |
0x80000000` from the packed ref chunks at 0x80122F70 and stores through it (`sw v0, 4(a0)`). The producers are
`recordDeferredDrawRefVariant` 0x80008518, `emitAllocatedDLCommand` 0x8000888C and `reserveAndEmitDLEntry` 0x8000CD8C, each packing
`(s0 & 0xFFFFFF) | tag << 24`. A spill-resident referent would turn that store into a silent write 16 MB lower, into heap. In the
run, 529/532 packed 9892 pointers, all 0x80xxxxxx. Statically the referents live in the DL pool, whose limit global never holds a
spill pointer (s7316). Re-check this if the DL pool or a mesh owner ever moves to spill.

Never-executed sites (static, single-source):

| idx | site | verdict | reason |
|---|---|---|---|
| 513 | generateUnlockString 0x8006E668 | scalar | global 0x80130B4C & 0x7FFE00 unlock bits; siblings 512/514-516 executed nn |
| 518 | factor5SortedTableLookupWidePairRecord 0x80085F00 | scalar | same shape as executed 519: MusyX table +4 packed 24-bit value, top byte read separately |
| 526/533/534 | playerSnowSpeederInit / initPlayerCraftMovementMode / playerAtStInit | scalar | `lw 0xC; and 0xFEFFFFFF; sw 0xC` clears flag bit 24 |
| 527 | recordDeferredDrawRefVariant 0x80008518 | heap-only | same ring as executed 529/532 (heap 9892, spill 0) |
| 536 | renderUnlitMeshFaces 0x80011D8C | scalar | field +0x10 & 0xFFFFFF == 0x20202 mode test; sibling 535 ran 67M nn |

Verdict: 19 runtime-clean + 7 static = 26/26, **0 H-alias**. Classes A-D close the spill-pointer struct-field edge for top byte,
order, difference and truncation.

## Class E KSEG re-tags closed (s7322 static, evaluated)

`or/addu/xor d, x, K` with K a constant whose low 24 bits are zero and top byte 0x80-0xBF (tools/s7317_field_compare_census.py class E,
selftest PASS). A narrowed x (<= 24 bits) re-tagged this way would map a spill pointer onto heap. Whole program: **404 sites, 0 unclassified**
(the census exits 1 on any). Output scratch/s7317/field_census_s7322.txt.

| provenance | sites | verdict |
|---|---|---|
| fpu (mfc1) | 387 | scalar: float->unsigned idiom. Checked separately: 385 have trunc.w within 3 instructions before the mfc1, 1 neg.s, 1 libultra cvt.w.d + FCSR in guPerspectiveF |
| index (sll < 8) + `lw off(d) ; jr` | 8 | jump tables at 0x80000000+off (quatFromCardinalAxis, decodeRdpFormat/SizeFlags, parseImageFile, loadTextureTile, inflate x3) |
| word (full lw) | 4 | spill-equal by evaluation: or/xor/addu with 0x80000000 leaves bit 24 alone (partitionFramebufferMemory osMemSize, processSongByHandle flag, renderLitTexturedMeshFaces sign flip, npcAtAtUpdate flag) |
| D | 1 | paired: commitMeshDrawBatchRefs `(ref & 0xFFFFFF) | 0x80000000` = class-D idx 528; runtime 0 spill sources at L4 (s7321), L1, L12 (s7321_trunc_levels soak) |
| other/narrow, read by hand | 4 | relocateSndPointer xor 0x80000000 / 0xB0000000 != 0 tests = s6993 mask site 0x800925FC (already patched); renderLitMeshFaceGroup 0xBD000000 \| byte = F5 DL command word |

Constants with nonzero low 24 bits (`lui 0x8013 ; addu at, at, idx` global-table indexing) are counted, not classified: index 2225,
other 577, narrow 194, word 29, fpu 1. They add an index to a global base, not a re-tag.
Verdict: **0 H-alias.** Classes A-E close the spill-pointer edge for top byte, order, difference, truncation and re-tag.

## Class F address-derived table index closed (s7323 static, evaluated)

`srl/sra d, s, k` (8 <= k <= 22; `--top` adds 23..31) of a non-constant whose result, scaled, reaches a memory base directly or
through `addu` with a constant or register base (tools/s7323_addr_index_census.py, linear fall-through scan per function, planted
selftest 6/6 incl. a segment-table ALIAS positive and a bounded negative). Each pointer-capable site is EVALUATED: every heap
(0x80000000-0x807FFFFF) and spill (0x81000000-0x813FFFFF) pointer is run through `(p [& srcmask]) >> k [& andimask]`; k <= 22 is
OVERFLOW when a spill index exceeds the largest heap index, k >= 23 (or a source mask above bit 24) is ALIAS when spill and heap
indices differ. Exit 1 on any unclassified site.

| verdict | 8..22 | 8..31 | meaning |
|---|---|---|---|
| scalar | 24 | 36 | narrow source: lhu/lbu/andi, sll16+sra (halfword sign extend), mfc1/mflo |
| bounded-safe | 20 | 20 | andi/and mask after the shift: every spill index lands inside the heap index range (hash/bucket) |
| spill-equal | 0 | 5 | top-byte index whose outcome is the same for heap and spill (bit 31, bits 25-27/28-31 of a flags word) |
| known (hand) | 17 | 20 | evaluator said probe/OVERFLOW/ALIAS/bounded-check; source read: ADPCM header bytes (2), 23-bit pan fraction (4), JPEG 16.16 coords (6), material flags 3-bit field 0x01C00000>>20 (appendRdpStateDl, sibling field 0x0E000000>>23), HOB record length 0x3F000000>>22 (loadSkyHorizonHob), float->int (processSceneNode), instruction-word decoder and COP2 result in data_gap_80024A0C, sound-macro 16.16 curve/volume and glyph code with sltiu range checks (3) |
| unclassified | 0 | 0 | |

No address-derived index takes a heap/spill pointer. Coverage limit: the scan follows fall-through order and stops at
redefinition and calls; an index that crosses a branch join or is passed to a callee is not seen (same limit as classes A-E).
Classes A-F close the spill-pointer-as-value edge. Open edge: whether the RCP (RSP DMA / DL segment addresses, 24-bit) is ever
handed a spill block (scratch/agent/NEXT.md, class G).

## Class G: RCP-visible spill references (s7324)

Question: does the RSP (DMA) or RDP (image commands) ever get a spill-block address? A spill pointer reaching the RCP either keeps
bits 24+ ("direct": hardware and rsp.hpp `& 0xFFFFF8` drop them) or was masked first ("alias": reads phys 0x00xxxxxx = heap/static).
Instrument `ROGUESQ_S7324_RCPREF=1|ctl` (src/rsp/s7324_rcp_spill.cpp) classes every RSP DMA (raw DRAM_ADDR before the runtime mask,
gfx/audio bank, rd/wr, IMEM excluded) and every SETTIMG/SETZIMG/SETCIMG in the hardware DPC stream against the s7317 allocation map.
Report `tools/s7324_rcp_report.py` (exit 1 on direct hit, failed control or foreign-tag alias). Control (ctl): once per second the
lowest live spill block is classed in its direct (& 0x1FFFFFFF) and masked (& 0xFFFFFF) forms: 198/198 each (68 s had no live spill).

| source (dd8 21:9 L4, 205 s flight) | total | direct | alias-only | alias+heap | notes |
|---|---|---|---|---|---|
| RSP DMA read gfx | 51.5M | 0 | 22742 | 0 | all static: ucode_data 0x80038D00 (tag 00), sub-DL 0x80037658/0x80037780 |
| RSP DMA read audio | 1.47M | 0 | 81383 | 942022 | static audio ucode_data 0x800A4E00; 40k heap-gap sample reads (tag 80) |
| RSP DMA write gfx/audio | 411M / 87k | 0 | 0 | 62502 | alias+heap = inside a live heap block |
| RDP image cmds | 40.0M | 0 | 0 | 0 | none ever below 4 MB alias range or above 16 MB |

The 2 MB grid cell array spill block at 0x81000000 makes everything below 0x1E000C "alias", so alias-only is only a triage bucket:
no alias-only hit carries a 0x01/0x81 tag, and a spill pointer can only become a 0x80-tag address by a class D/E mask + re-tag (closed,
0 spill sources at runtime). Verdict **H-cpu-only**: no RCP-visible address is a spill block. Open datum: heap-gap audio reads.

## Class H: the frame-buffer layout bound and its consumers (s7335 static + runtime)

`tools/s7335_fb_bound_census.py` (exit 1 = unclassified, exit 2 = positive control failed) tracks `lui`-based addresses across
RecompiledFuncs. It lists every access to the partition globals 0x801163D8..0x801163F8 (0x801163E4 = the persistent-arena hi),
the heap globals 0x8010FF00..0x8010FF1C, osMemSize loads, KSEG0-top `lui`s and 24/23-bit masks. Control: the s7334-measured
sites 0x80001408 (scene coalesce hi) and 0x80000ED8 (bound writer) must be found. Run 2026-11-14: 68 sites, 0 unclassified.

| Group | Verdict |
|---|---|
| partitionFramebufferMemory 0x80000DD4 | top = cfg+0x44&0x2000 ? 0x80400000 : 0x80000000\|osMemSize; 63E4 = top - zbuf; 63D8..63F8 carved down from it (15 writers, 3 internal readers) |
| thread3_video_handle / runVideoFrameTick (13) | pass 63E4 as the coalesce hi and 63D8..63F8 as the video config: all straight from the partition |
| ensureHeapInitialized 0x80001930 | heap size = *63E4 - base (derived) |
| 0x8010FF08..FF14 (8 stores) | coalesce/initMainHeap args incl. the stored hi: WRITE-ONLY, no guest reader |
| 0x8010FF18 heap head (11), 0x8010FF00 free-list head slot (8) | walkers start at the head and stop at the fl=8 sentinel; buildHeapFreeList reads &FF00 offset 0 only |
| masks | commitMeshDrawBatchRefs = class D idx 528; renderFlat/UnlitMeshFaces 0xFFFFFF = 0x020202 flag compare; MusyX 0x7FFFFF scalars |

Guest verdict H-clean: no reader re-derives the heap/fb end from a constant, and nothing assumes the tail ends at 8 MB. Tail end
= 0x80000000|osMemSize <= 0x81000000 because librecomp clamps OSMEM_MB to 4..16. Second line: s7334's runtime boot sentinel
0x80B69FF0 = 0x80C00000 (OSMEM 12) - 0x96000 (640x480x2) - 0x10, the same number the formula gives.

**Host H-overlap (real, latent, FIXED s7335):** the DLPOOLX bump arena is [0x81000000 - DLPOOLX_MB, 0x81000000). With the dd>1
bundle (OSMEM 12, DLPOOLX 4) it starts exactly at the guest top 0x80C00000. DLPOOLX_MB 5..8 (the code allowed up to 8) or OSMEM_MB 13..16
handed the guest fb tail and heap top to the DL chunk pool. Run (L1 dd8 21:9 forced, 131 s each, scratch/s7335/run.txt):
DLPOOLX_MB=8 with the clamp off put chunks at 0x80800000 (inside the heap, which ends at the 0x80B6A000 sentinel). It held
131 s without a crash, so the defect is latent. Fix (src/main/upstream_compat.cpp rs64_s7335_dlpool_cap): the arena never starts
below the guest top. `[s7335] dlpool ...` line at the first grow, ROGUESQ_S7335_CLAMP=0 = old. Default arm identical (80C00000, 4 MB).
The legacy spill base 0x80800000 under OSMEM>8 with SPILL_HI=0 now prints a `[s7335] WARNING`.

## Class R: hard-coded 8 MB guest-range bounds (s7337 static + runtime)

Since s6858 every dd>1 run tells the game it has 12 MB (guest top 0x80C00000, rs64_ram_top up to 0x81800000 with s7336 arenas).
Census: `tools/s7337_bound_census.py [--controls]` (literals 0x80800000 / 0x807FFFxx; exit 1 = generated survivor or unclassified host site).

| part | sites | class | verdict |
|---|---|---|---|
| host, env-gated logging/probes (m5_*, f5 shadow, s5229, floor writer, g5b trigen, createmq row cap, port-load log) | 32 | D | stale bound only drops log lines |
| host, deliberate arena layout (s6086 divert, s6558 cut, s6909/s7335/s7336 comments+code, s6993 okb) | 5 | A | intended |
| host comments / `rs64_ram_top` initial value | 6 / 1 | C / I | n/a |
| host osSpTaskStartGo OSTask check (rs64_guest_range_valid) | 4 lit, 1 fn | B | fixed s7337 |
| generated funcs_*.c survivors of fixup_ramtop (s6311 edgefade/s6325 radfade, s6417 meshlog, s6657, s7101, s5818 `ull`) | 11 lines / 13 lit | G | converted; all opt-in, latent |

B detail: `addr >= kseg0_base && size <= kseg0_end - addr` wraps for addr > kseg0_end, so the pre-s7337 check accepted every
sign-extended pointer above 8 MB (positive control: synthetic 0x80900000 -> old=1). The stale literal was therefore never a drop
risk at dd>1, but the check guarded nothing at the top either. Now `addr < end` first, end = rs64_ram_top (ROGUESQ_S7337=0 = 8 MB).
Startup `[s7337] selftest` + power-of-two `[s7337] task range: n= hi= top= widened=` lines. Runtime (forced L1, FPS60):
dd1 and dd8 21:9 real task pointers max 0x80149470, widened=0, 0 s7197 drops; dd8 hold 137 s flight, 0 crash.
G detail: fixup_ramtop runs last in fixup_game_funcs_vendored.py, but scripts applied straight to the live tree afterwards emit raw
literals. The census catches that; the radfade/edgepos camera bound was in range at dd1 and dd8 (cam=0,0 rows 0/5365 and 0/7676).
Open: class M, 193 physical 8 MB masks/ends (`& 0x7FFFFF`, `< 0x800000`) counted by the census, not yet classified.
