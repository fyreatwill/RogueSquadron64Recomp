# NEXT work unit (resident-0C overlay splice and route validation)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

The s738 static audit selected stale-main-image: overlay 12's correct
`L_1DB0` is a distinct ROM-backed TriGen implementation, while the live
router falls through to the main bootstrap block that clears `DMEM[0x152]`.
Land one regeneration-safe splice for resident 0C, patterned after the
existing resident-04 clip splice, then validate it in the section-2 phase.

## Competing hypotheses

- **H-splice-correct:** routing resident 0C to the generated overlay-12 code
  removes the observed `L_1DB0` depth reset and its paired depth-0 reuse.
- **H-ovl12-return-incomplete:** overlay 12 has generated indirect targets or
  resident helpers that are not wired by the splice, producing an immediate
  controlled `UnhandledJumpTarget` or build-time extraction failure.
- **H-reset-independent:** the reset/reuse remains after a live overlay-12
  route, so another writer/path causes the plateau defect.

## Discriminating measurement

One build must include both the new route counter and the existing reset/reuse
ledger. In a phase-latched section-2 run, live `OVL12_*` route markers plus
zero active reset/reuse rows select H-splice-correct. A build/extraction error
or a route-specific unhandled target selects H-ovl12-return-incomplete. Live
OVL12 markers plus retained reset/reuse selects H-reset-independent. The
resident-04 `CLIP_*` route must remain live in the same build as a positive
control; do not accept a zero reset result without it.

## Commands

    python3 tools/make_clip_composite.py 4
    python3 tools/make_clip_composite.py 12
    ../N64Recomp/build/RSPRecomp factor5_rsp_ovl4.toml
    ../N64Recomp/build/RSPRecomp factor5_rsp_ovl12.toml
    python3 tools/fixup_factor5_ucode.py build/factor5_ucode/factor5_ucode_recompiled.c
    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    # Queue a self-contained phase-latched section-2 recipe; do not babysit it.
