# NEXT: ATTRIBUTE THE SOURCE BAND TO A WRITER CLASS
HYPOTHESIS-ID: g3-hangar-artifacts

Checkpoint close-out: s6606 selected H-source. The source band is present
before presentation in the clean 16:9 arm; the 21:9 route was not reached and
must not be treated as a null. Do not rerun the source fingerprint.

Work unit: add one phase-gated writeback-range census at RT64 colour
writeback, then run one retail control and one ASPECT 16:9 arm in the same
Debug build. Join each writeback range to the measured source-band columns
269..335 and the same hangar phase; keep `[fb-source-fp]`, `[fb-flip-range]`,
and `[fbdump]` enabled. Exact discriminator: an intersecting colour
writeback range before the source fingerprint selects H-RDP-writeback; a
clean writeback census with the source band still present selects H-game/
guest-write. The source fingerprint is the positive control, and the retail
arm must fire its phase control. Do not add a guard, skip, or default change
until the writer class is named.

Competing hypotheses:

- H-RDP-writeback: RT64 colour writeback covers the measured band before the source copy.
- H-game-write: no RT64 writeback covers it; the guest/RDP stream wrote the band directly into the source framebuffer.
- H-range-join: the band is covered, but the current writeback census misses it because of row/stride or phase attribution.

Discriminator: one same-phase intersecting-range table, with the source
fingerprint and retail control firing in the same run. The retail oracle
remains unavailable because its built core/plugin dylib is absent locally.

Exact preparation/build commands:

```sh
rg -n 'rs64_writeback|wblog|colorWriteWidth|source\[=' lib/rt64/src/hle/rt64_state.cpp
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
```

Do not add a guard, skip, or default change until the writer is named and its
value is shown to be illegitimate.
