# NEXT: RESUME the source-pixel discriminator for the wide-only hangar band
HYPOTHESIS-ID: g3-hangar-artifacts

Checkpoint close-out: s6603 completed the copy/flip witness and ruled out a
malformed wide stride. Do not rerun that experiment. The next work unit is to
add one phase-gated source-pixel fingerprint immediately before
the existing `present.storage` memcpy, then run the saved s6603 arms in one
build: `scratch/agent/m6/s6603_retail`,
`scratch/agent/m6/s6603_wide16`, and `scratch/agent/m6/s6603_wide21`. Their
existing `mc_ctl.txt` and framebuffer captures are the route/phase reference;
preserve the same route settings when launching each arm. Keep `[fbdump]`, `[vi]`, and
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

Exact preparation/build commands:

```sh
rg -n 'screenFbBytes|present\.storage|FB_DUMP|VI_ORIGIN|viewport|scissor' lib/rt64/src/hle/rt64_state.cpp src/main
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
# Launch the three saved route arms from build/ with their s6603 settings,
# writing captures under scratch/agent/m6/s6604_sourcefp/{retail,wide16,wide21};
# SIGKILL cleanup. Do not interpret a null unless all phase controls and the
# retail positive-control dump fire.
```

Do not add a guard, skip, or default change until the writer is named and its
value is shown to be illegitimate.
