# Next work unit

HYPOTHESIS-ID: m5-retail-publication-boundary

Run one bounded retail-only writer attribution capture. The s4933 parity join
qualified all controls and both mission origins, but the retail task-entry
watch saw 643 type-2 rows only at hangar `0x006AB400` and zero at
`0x00690400`/`0x00620400`, while the port produced fresh task handoffs at both.
Watch the known retail task-state writer `0x80091784` at the same mission
origins. Do not change runtime behavior.

Competing hypotheses and discriminator:

1. H-writer-attribution: `0x80091784` fires at a mission origin, so the task
   publication exists and the old `0x80033FCC` execution watch is too narrow.
2. H-retail-absent: all whole-RDRAM, VI, hangar-task, and mission-origin
   controls pass, but `0x80091784` has no mission-origin hits; retail lacks the
   port's fresh publication on this route.
3. H-capture-invalid: any positive control fails, so the mission null is not
   interpretable.

The discriminating table is writer-PC hit count and task fields at each origin:
hangar `0x006AB400`, first mission `0x00690400`, and following mission
`0x00620400`. A qualified writer hit selects H-writer-attribution; a qualified
writer null selects H-retail-absent; a failed control selects H-capture-invalid.

Run:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 240 --vi-poll --vi-trace --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,56:start,66:start,76:start,86:start,96:start,106:start,116:start,126:start,136:start,146:start,156:start,166:start --watch-write 0x0:0x800000 --pc-phase-log-width 0x6AB400:512 --watch-pc 0x80091784 --pc-task-dump 0x80033FCC --pc-task-type 2`

Inspect only bounded controls and writer/task rows grouped by origin. No
mitigation is authorized from a null or mismatch without naming the writer and
proving the value illegitimate.
