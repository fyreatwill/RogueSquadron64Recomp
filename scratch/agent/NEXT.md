# NEXT: attribute the wide-only hangar bands to framebuffer stride
HYPOTHESIS-ID: g3-hangar-artifacts

One work unit: add one phase-gated witness for the framebuffer copy/flip path,
then run the retail 4:3, ASPECT 16:9, and ASPECT 21:9 hangar arms in one build.
The witness must log VI width/origin, selected framebuffer, row stride, and the
source/destination range used by the wide framebuffer path. Keep the current
`[fbdump]` and `[vi]` controls enabled; the retail arm is the positive control.

Competing hypotheses:

- H-stride: the wide framebuffer row/flip stride or source range leaves stale
  data in the measured band.
- H-viewport: the viewport/scissor is fixed incorrectly and exposes a band at
  a screen-space boundary.
- H-rdp: the RDP/RT64 edge treatment produces the band after the source image
  is already correct.
- H-game: the submitted hangar geometry or texture itself contains the band.

Discriminator: a logged source range or stride that overlaps the measured
16:9 x=269..334 band or 21:9 x=347..639 band selects H-stride; identical
stride/source with a fixed screen-space boundary selects H-viewport/H-rdp;
identical source geometry and pixels in retail and wide arms selects H-game.
Every null requires the retail phase/dump positive control in the same run.

Commands:

```sh
rg -n 'FB_WIDTH|FB_DUMP|VI_ORIGIN|stride|copy|flip|scissor|viewport' src lib/rt64
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
# Run the three s6602 route arms with the new witness and SIGKILL cleanup.
```

Do not add a guard, skip, or default change until the writer is named and its
value is shown to be illegitimate.
