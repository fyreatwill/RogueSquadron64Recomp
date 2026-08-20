# SUBSTITUTION — s2004 payload-hash census (2026-08-20)

## 1. What specifically stopped the planned unit from running

The primary session died mid-work-unit (usage limit or turn cap) before any
payload-hash code was written to `librecomp/src/rsp.cpp` or
`ultramodern/src/audio.cpp`, before the patches were exported, and before
any build or game run was launched.

## 2. Evidence THIS ITERATION that it was actually stopped

- `PORTING-STATE.md` contains no Session 2004 entry (only through 2003).
- `git diff HEAD` shows only dirty submodule pointers (no new source lines).
- `grep -n "payload\|nz_count\|nonzero_b\|queue_samples.*hash"` in
  `lib/N64ModernRuntime/librecomp/src/rsp.cpp` and
  `lib/N64ModernRuntime/ultramodern/src/audio.cpp` returns zero matches.
- No `scratch/agent/s2005-*.log` or `scratch/s73_post_a_scene/m5-audio-step5-*`
  files exist from this session.
- `submodule-patches/N64ModernRuntime.patch` line count matches session 2003's
  exported state; no new lines were added and exported.

## 3. The single experiment that would REFUTE the blocking explanation

If `lib/N64ModernRuntime/librecomp/src/rsp.cpp` contained `payload_fnv` and
`payload_nz` fields (or any hash computation over `rdram[dram..dram+len]`
after the DMA write), that would refute the claim that code was not written.
Running `grep -n "payload_fnv\|payload_nz" lib/N64ModernRuntime/librecomp/src/rsp.cpp`
returns empty, confirming the stopping explanation.
