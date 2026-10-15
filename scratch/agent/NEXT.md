# Next work unit

HYPOTHESIS-ID: m5-retail-writer-target

Run one bounded retail-only writer-context capture. s4934 passed the
whole-RDRAM and VI controls and found writer `0x80091784` at both mission
origins, but the old `0x80033FCC` task-entry watch remained zero. Capture the
writer's register/field context at hangar `0x006AB400`, first mission
`0x00690400`, and following mission `0x00620400`. Do not change runtime
behavior.

Competing hypotheses and discriminator:

1. H-task-writer: mission-phase field rows expose a stable task-like pointer
   and changing task/value fields, so `0x80091784` is the publication boundary.
2. H-auxiliary-writer: mission-phase rows expose stable non-task context or
   cadence fields, so the writer is related but not the OSTask publisher.
3. H-capture-invalid: whole-RDRAM or VI controls fail, so field nulls are not
   interpretable.

The discriminating measurement is the bounded `--pc-field-dump` table at
`0x80091784`: compare `s0`, `s1`, `MEM_W(s0+0x60)`, `MEM_BU(s0+0x22)`, `$v0`,
and `MEM_HU(s1+0x22)` by the three 512-wide origins. A task-like mission row
selects H-task-writer; stable auxiliary context selects H-auxiliary-writer; a
failed control selects H-capture-invalid.

Run:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 240 --vi-poll --vi-trace --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,56:start,66:start,76:start,86:start,96:start,106:start,116:start,126:start,136:start,146:start,156:start,166:start --watch-write 0x0:0x800000 --pc-phase-log-width 0x6AB400:512 --watch-pc 0x80091784 --pc-field-dump 0x80091784 --pc-task-dump 0x80033FCC --pc-task-type 2`

Inspect only bounded controls and field/task rows grouped by origin. No
mitigation is authorized from a null, mismatch, or wild value without naming
the writer and proving the value illegitimate.
