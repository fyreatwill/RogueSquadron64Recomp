# NEXT work unit (s1968) — hangar hologram-beam artifact: H1 blend/z census

HYPOTHESIS-ID: hangar-hologram-beam-artifact

## What s1967 settled

H2 (a malformed/corrupted triangle command reaching the RDP queue) is
**REFUTED** for the hangar hologram-beam visual artifact. Built a
writer-attestation hook at the actual `L_1930` header-byte store
(`sb $10, 0x0($16)`, `tools/fixup_factor5_ucode.py` Fixup 21 +
`rs64_m4_y8000_store` in `src/rsp/dpc_bridge.cpp`) that marks a
per-offset `stored[0x1000]` bitmap, cleared after each flush drains
`[0xD60, end)`. Result
(`scratch/agent/soak_results/s1968_hangar_tri_dump_20260818-090536/`):
every one of 14 sampled `YH<=YM<=YL`-violating "triangle" commands had
`stored=0` (never written that cycle), while every ordinary
well-formed triangle showed `stored=1` (same-run positive control that
the attestation bitmap actually works). The commands flagged bad in
s1967's first pass were reading stale, previously-used DMEM bytes that
`r16`'s write-pointer happened to still cover — not a real defect.
Do not re-open H2 without a new, different anomaly (this exact
instrument is now closed on this question).

## What's still open

- **H1 (blend/z-compare mismatch).** RT64's HLE may set the wrong RDP
  blend mode or z-compare state for the beam-cone draw. The Fill
  Triangle command's own fields (checked in s1967) carry no blend/z
  information — that lives in separate `SETOTHERMODE_L_EX` (`0xB3`)
  and `SETOTHERMODE_H_EX` (`0xBE`) commands per
  `docs/F5-UCODE-REFERENCE.md`'s command table. Untested so far.
- **H3 (legitimate retail design).** Still unresolvable by
  instrumentation — confirmed twice now (s1967) that the oracle has no
  screenshot capability and its RSP-HLE plugin never executes guest
  `L_17F0`, so there is no independent pixel or geometry ground truth
  to check this against. Do not keep re-confirming this; it's settled
  as "cannot check," not "assumed false."

## Discriminator to build next (H1 probe)

The M4/`0xD60` flush walker (`rs64_m4_y8000_flush`) only recognizes
`0xC8`-class (`0xC8-0xCF`) triangle headers and skips everything else
by 8 bytes. Extend it (or add a sibling hook) to ALSO recognize and
dump `SETOTHERMODE_L_EX`/`SETOTHERMODE_H_EX`-class RDP commands in the
same hangar-gated `[0xD60, end)` stream — these are standard 8-byte RDP
commands (opcode + mask/set words), not part of the F5-specific
inline-data commands `docs/F5-UCODE-REFERENCE.md` warns about (that
warning is about the *original* F5 display list, upstream of this
restage buffer, which by s1840/s1856/s1967 is established to already
be plain RDP-format bytes).

1. Identify the RDP opcode bytes for `SETOTHERMODE_L`/`SETOTHERMODE_H`
   in standard hardware encoding (not the F5-custom `_EX` wrapper,
   which is what F5Rogue.cpp's ucode-side handler consumes before
   restage — the RESTAGED byte in this buffer should be the plain RDP
   opcode). Cross-check against `docs/F5-UCODE-REFERENCE.md` and, if
   needed, a quick grep of RT64's `rt64_gbi_f3dfactor5.cpp` HLE path
   for how it encodes these after translation.
2. Add a dump (reuse the `ROGUESQ_LOG_M4_TRI_DUMP` gate or a new flag)
   that logs every `SETOTHERMODE` command's mode bits alongside the
   existing triangle dump, so blend/z-compare state can be read
   directly adjacent to the triangle commands in stream order —
   the state active when the beam-cone triangle(s) draw is whatever
   the most recent preceding `SETOTHERMODE` set.
3. Same hangar recipe (`scratch/agent/soak_queue/done/
   s1950_hangar_yield_repro_*.sh` as template, add the new dump flag).
   Same ~4s window budget.
4. Compare the blend/z mode active around the triangles at the known
   `0xE80`-region area (now confirmed stale/irrelevant — the REAL
   beam-cone triangles are elsewhere in the stream, likely near
   `0xD60` given most triangles land there) against what a correctly
   alpha-blended translucent primitive requires (`Z_CMP`/`Z_UPD` off
   or blended, `CVG_X_ALPHA`/`ALPHA_CVG_SEL` set appropriately per
   standard RDP other-modes semantics) — a mismatch selects H1.

## If this doesn't discriminate cleanly in one session

Per iteration budget rule 8: this is a NEW probe within the same
hypothesis thread (s1967 was H2; this is H1) — not yet a stalled
iteration. If the H1 census also comes back ambiguous or clean, write
the hypothesis/evidence table explicitly here and treat H3 as the only
remaining explanation (unresolvable, not refuted) — at that point this
item likely drops in priority since no further instrumentation is
available for either survivor.

## Do not repeat

- Do not re-run the H2 (`tri_order_bad`) check expecting a different
  answer — it's settled (REFUTED, same-run positive control, 14/14
  agreement).
- Do not conflate this with the closed M4 Y=`0x8000` accumulator
  question (`y8000_any=0` again in s1967) — different mechanism,
  different offset, do not re-walk VMADH/VGE.
- Do not point the oracle at DMEM `0xD60` — confirmed (twice now) the
  RSP-HLE plugin never executes guest `L_17F0`.
- Do not resume the generated-symbol sweep (closed, 57 RE/hold left,
  s1966).
- Cross-run A/B on this scene without phase-gating still forbidden —
  the hangar window is ~4s of animating content.
