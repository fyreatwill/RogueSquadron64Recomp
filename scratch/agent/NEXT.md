# Next work unit: M5 Step 7 descriptor-selector writer census

HYPOTHESIS-ID: m5-step7-descriptor-selector-writer

Session 4095 selected Htuple-diverge: retail normal-tail rows carried selector
values 1..7, while the port pointer/branch rows carried selector 0. Entry and
tail were live on both sides and all eight returns stayed zero. Do not change
or remove the returns.

Competing hypotheses:

- Hwriter-live: a target-phase retail writer changes the selector field and its
  PC can be named.
- Hselector-absent: the selector field is never written in the qualified retail
  route; the observed values are pre-existing state.
- Hcoverage: the whole-RDRAM control or one of the target phase gates is absent.

Discriminating measurement: arm the retail oracle's physical write watch over
the dynamic `s1+0x22` selector span observed in s4095 (`0x1714F0:0x1728C0`),
with `--pc-hist-watch` and title/hangar `--pc-hist-phase` buckets. A
phase-qualified writer PC and selector transition selects Hwriter-live; zero
target writes with both controls selects Hselector-absent; missing controls
select Hcoverage.

Exact starting command to add to a self-contained driver:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x1714F0:0x1728C0 --pc-hist-watch 1 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --vi-trace`

Run from the repo root with the positive-control and phase markers checked.
This is one oracle-only ground-truth work unit; do not alter generated returns
or add a port replacement until the writer PC is identified.
