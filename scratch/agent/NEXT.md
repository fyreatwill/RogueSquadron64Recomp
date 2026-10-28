# NEXT: resume the source-pixel discriminator for the wide-only hangar band
HYPOTHESIS-ID: g3-hangar-artifacts

Checkpoint close-out: s6603 completed the copy/flip witness and ruled out a
malformed wide stride. Do not rerun that experiment. The next work unit is to
add one phase-gated source-pixel fingerprint immediately before
the existing `present.storage` memcpy, then run retail 4:3, ASPECT 16:9, and
ASPECT 21:9 hangar arms in one build. Keep `[fbdump]`, `[vi]`, and
`[fb-flip-range]` enabled; the retail arm is the positive control. Fingerprint
only the measured band and its matching rows: first/last changed x,
nonzero/color-transition count, and a compact hash of source pixels. Do not
dump run-lifetime data.

Competing hypotheses:

- H-source: the game/RDP-produced source framebuffer already contains the band.
- H-viewport: the source is clean, but a fixed screen-space viewport/scissor
  boundary exposes it in the displayed output.
- H-rdp: RT64's RDP/presentation path introduces the band after the source copy.
- H-width: the source pattern is identical across widths, but only wide output
  shows the band because of a width-dependent presentation transform.

Discriminator: band pixels in the source before `memcpy` select H-source;
clean source plus band in the owner-visible output selects H-viewport/H-rdp;
identical source hashes across arms with a wide-only displayed band select
H-width. Every null requires the retail phase/dump positive control in the same
run. The retail oracle remains unavailable because its built core/plugin dylib
is absent locally.

Exact commands:

```sh
rg -n 'screenFbBytes|present\.storage|FB_DUMP|VI_ORIGIN|viewport|scissor' lib/rt64/src/hle/rt64_state.cpp src/main
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
# Reuse the saved s6602 route arms; run all three with the witness and SIGKILL
# cleanup. Do not interpret a null unless all phase controls and the retail
# positive-control dump fire.
```

Do not add a guard, skip, or default change until the writer is named and its
value is shown to be illegitimate.
