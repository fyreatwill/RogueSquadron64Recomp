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
| s4563 `fp == 0x80179380` + `head in 0x80179380..0x8017970C` | 1 | Heap literal, default ON, but DEAD: see below |
| FS slot 0x76DF60 | 4 | Heap literal, opt-in only (LOG_FS_SLOT, FS_PIPE_INJECT default off) |

## s4563 stale-head skip is dead

The check survives in musyxSynthFrame but its setter does not: `g_s4563_blk_freed` is only ever read. The setter sat inside the
`s4561 order` block in rs_free, anchored on the `s4300 rsfree bt` log line, and neither marker is in the live funcs_0.c. Even
when present it needed ROGUESQ_LOG_RS_FREE (s4565). The hazard is covered by s4786 PAUSE=4 (default on), which holds synth from
teardown to audio re-init by hook position, so it does not depend on the heap address.

## Replayed patches missing from the live tree

`tools/audit_heap_addr_tests.py` lists 9 replayed scripts whose MARK is absent (s2463, s4221-3, s4300, s4466, s4560, s4602, s4680).
All 9 are probes or logging (each script's docstring read; s4680 and s2463 are store/callback watches); why they are absent after a replay that fails on error was not established.

## Runtime check (21:9 + FPS60 + dd4, spill at 0x81000000, ROGUESQ_HUD_LOG=1, same binary)

| Level | vp 0x80138D20 elements | Heap HUD table | Reticle (static) | [s4562] pause set | [s4563] lines |
|---|---|---|---|---|---|
| 1 (control) | 10 | 0x805622CC..0x8056241C | 0x8010CA58/88 | 6 | 0 |
| 10 (control) | 10 | 0x8028FD3C..0x8028FE8C | 0x8010CA58/88 | 7 | 0 |
| 5 (264 s hold) | 10 | 0x8055D2FC..0x8055D44C | 0x8010CA58/88 | 7 | 0 |
| 14 | 20 | 0x8055BB5C..0x8055BF04 | 0x8010CA58/88 | 6 | 0 |

The table moves by level and always stays above the 0x80110000 bound; heap starts at 0x80154690, so it cannot fall below it.
A 131 s lvl5 hold logged 0 elements (still in its cinematic), so that arm was discarded and re-run. All arms alive, 0 stalls, 0 crash lines.
