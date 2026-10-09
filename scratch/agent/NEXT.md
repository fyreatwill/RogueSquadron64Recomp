# Next work unit (s4347): earlier C904 input-source attribution

HYPOTHESIS-ID: m5-step9-earlier-input-source

The s4346 retail witness passed whole-RDRAM, title `0x00790400`, hangar
`0x006AB400`, and exact C904/reader execution controls. Neither the selected
word at `0x8009C950` nor the first two words at the C904 input pointer carried
the retained `0x0010/0x3108` family. The next boundary is caller `0x8009C0E4`
and the producer of its input pointer.

Competing hypotheses:

- H-caller: the caller transformation at `0x8009C0E4` carries the retained
  family; phase-gated caller registers/input values will contain `0x0010` or
  `0x3108`.
- H-input-producer: the caller only forwards a non-family buffer; a writer to
  the input-buffer span carries the family and identifies the producer.
- H-earlier-source: neither caller nor watched input-buffer writer carries the
  family, moving the boundary earlier again.

Discriminating measurement: one batched retail oracle witness for execution at
`0x8009C0E4` plus a phase-gated writer watch over the exact input-buffer span
derived from the generated caller. Record caller `$v0/$a1/$a2/$a3`, input
pointer and first words, writer PC/source value, and family classification.
Caller-family with no matching writer selects H-caller; writer-family selects
H-input-producer; neither selects H-earlier-source. The whole-RDRAM watch must
fire first, and title/hangar/C904 controls must all pass.

Before building, inspect `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`
around `0x8009C0E4` and the input-buffer consumers. Add the batched witness to
`tools/oracle/rs64_oracle.c`, then build once:

`env CORE_SRC="/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core" bash tools/oracle/build.sh`

Run from the repo root for 180 seconds with the debug core, `build/rogue_squadron.z64`,
Rice video, whole-RDRAM watch, title/hangar phase buckets, C904 execution
control, and the standard schedule:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom build/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 180 --watch-write 0x0:0x800000 --hit-cap 10000 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150`

Do not alter decoder/RSP/AI behavior or add a mitigation.
