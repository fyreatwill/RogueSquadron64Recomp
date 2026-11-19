# Class MK8 — 8 MB physical-address keys at dd>1 (s7648)

**Verdict: CLOSED, H-mk8-diag-only. 0 behaviour fixes.** Every 8 MB-masked address, every 8 MB physical-end check, and
every 0x807Fxxxx near-variant guest bound in host, lib and generated code sits in a diagnostic/opt-in path. No default-on
lookup, guard or key aliases (or rejects) dd>1 data above 8 MB.

## Why this class exists
At dd>1 the owner bundle (OSMEM 12 heap, DLPOOLX arena, spill arena 0x80800000..0x81000000) puts live guest data at
phys >= 8 MB. The RSP reads with rs64_s7327_mask 0x1FFFFF8 and the CPU with 0x1FFFFFFF (TO_PTR widened s6572). A key
`& 0x7FFFFF` therefore **aliases** a high address onto low RAM, and a bound `< 0x800000` / `< 0x807FFF00` **rejects** it.
s7647 lost a lead (TS-4) to exactly such a key. Class R (literal 0x80800000 bounds) was closed s6132/s7337
(`fixup_ramtop.py`, `s7337_bound_census.py`), which listed masks only as "class M, open" and whose generated-tree
pattern does not match 0x807Fxxxx.

## Census (`python3 tools/s7648_mk8_census.py [-v] [--controls]`, exit 1 on any unclassified site)
| Scope | Pattern | Sites | Class |
|---|---|---|---|
| Host src/ + lib (ultramodern, librecomp, rt64 hle/gbi/render) | `& 0x7FFFFF`, `0x007FFFFF`, phys end `0x800000` | 229 | D 177 (env/enabled-gated function), D* 52 (hand-reviewed, below) |
| Generated RecompiledFuncs + build/factor5_ucode | masks + `0x807Fxxxx` | 25 | D 17 (opt-in/diag patch blocks), F 8 (float mantissa masks) |
| ucode (factor5_ucode/*.c) | — | 0 | — |

D* (always called, but the 8 MB value only feeds diagnostic state/prints; each read in full s7648):
- main.cpp: rs64_m5_pcm_writer_dma (g_rs64_pcm_last_dma_phys, printed only), rs64_s4457_list_check (audio-node shadow
  scan, arena < 8 MB), rs64_s5229_store/entry (diag tables), rs64_m5_host_write_census / rs64_s6843_store (rs64_vsrc_*
  armed by log env), rs64_m5_audio_input_dma, rs64_m5_pcm_writer_snapshot, rs64_audio_hash_rdram, start_fl_zero_poller,
  rs64_filter_voice_guest_span_ok/hash (LOG_FILTER_VOICE_AUDIT).
- dpc_bridge.cpp: rs64_f5_vtxcolor_state (read back only in rt64_gbi_rdp.cpp shade-diag prints), rs64_e9prov_task_begin
  (root_dl consumed by prints/gated probes), rs64_inline_probe_trigen_stage, dlw_dump_words.
- librecomp rsp.cpp: the M5 audio join/probe instruments (audio_join_match, audio_image_match*, rs64_audio_join_image_*,
  audio_dma_overlaps, audio_hash_rdram, audio_read_rdram_word, rs64_s4209_read, rs64_probe_audio_dma_write
  [rs64_s4208_active], rs64_s4214_scan [LOG_S4213]); rs64_s4211_task is ungated but read-only hashing of the audio
  task's low-RAM dp block. print.cpp __osRdbSend size sanity; sp.cpp dump_frame RAM dump.
- rt64: `RDRAMSize = 0x7FFFFF` (rt64_state.h) sizes only the debug RDRAM fwrite dump; gbi_rdp shadeDl and gbi_f3dfactor5
  sites are shade-diag / HLE-only prints.
- s7644_rspdma.cpp rs64_s7645_gfx_read: the 8 MB key is the deliberate s7647 alias CONTROL.

Generated D sites: s4204/s4207/s4208/s4209 M5 audio rings (`if (!enabled) return;` blocks), s6363 heightfade (`en`, env
ROGUESQ_EDGE_FADE_R2_Y), s6660/s6663 objective response (ROGUESQ_OBJECTIVE_RESPONSE, G1(d) parked by owner).

## Controls
`--controls` plants an ungated `a & 0x7FFFFFu` host key and an ungated `a < 0x807FFF00u` generated bound in temp
files; both must be reported unclassified (s7648: planted=2 flagged=2 PASS). `s7337_bound_census.py` still exits 0.

## Limits
D is a regex on the enclosing function body (getenv / ROGUESQ_ / enabled / _on() before the site), not a proof that
the gate is off by default; the D* list and every always-on candidate were read by hand. **Diagnostic conclusions are
still at risk**: any CLOSED result that used one of these D/D* keys on dd>1 data may be an alias artefact like TS-4.
That re-validation is the follow-on (NEXT s7649).
