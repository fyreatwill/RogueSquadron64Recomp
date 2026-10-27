# G3c(b) spike lines: reference status (s6440)

Question: do the in-flight spike wedges also occur on retail hardware?

| Hypothesis | Evidence | Status |
|---|---|---|
| H-rsp-emu (our LLE RSP differs from hardware) | s6300 divide ROM matches; s6301 SIMD==SISD for all VU ops; s6385 FD57 ring replay 8/8; s6388 independent cxd4 scalar replay matches 24 accumulator lanes and independently yields FD57 | REFUTED (4 lines) |
| H-stale-slot (pinned vertex is unwritten data) | s6366 pinned vertex; s6373/s6374 not the VGE clamp; s6376-6378 it is computed in-ucode from a saturated near-zero-w clip ratio | REFUTED as a stale slot; it is a legitimate clip-intersect result |
| H-retail (hardware draws the same wedge) | needs an LLE RSP + RDP reference on lvl1/2 flight | UNRESOLVED: no reference available (below) |
| H-rt64 (RT64 draws out-of-range coords differently from RDP) | wedge x up to 1113.7 is representable in RDP s15.16 X / s11.2 Y, scissor clips on hardware; no measurement of RT64 vs RDP on it | OPEN, unmeasured |

Reference inventory measured this session (2026-10-27):
- /opt/homebrew/lib/mupen64plus holds rsp-hle, video-rice, video-glide64mk2, audio-sdl, input-sdl. rsp-hle does not execute the F5 microcode, so it never produces the RSP output that carries the wedge. Neither Rice nor glide64mk2 has an F5 path.
- ares, cen64 and simple64 are not installed; `brew list` shows only mupen64plus.
- The oracle reaches the attract demo (0x690800) and hangar only (tools/oracle/README.md), and only answers memory/CPU questions.

Conclusion: the vertex inputs and the RSP arithmetic are retail-faithful, so retail hardware almost certainly produces the same RSP output; whether the visible wedge survives the hardware RDP is not measurable here. `ROGUESQ_CULL_SPIKE` stays opt-in. Only a human install of an LLE reference (parallel-rsp/ares or GLideN64 with F5 HLE) closes H-retail; the cheaper local step is H-rt64: feed one logged wedge triangle through an RDP scissor/clamp model and compare to what RT64 drew.
