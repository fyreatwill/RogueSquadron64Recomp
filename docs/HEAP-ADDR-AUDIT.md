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
