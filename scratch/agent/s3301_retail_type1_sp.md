# Session 3301 — retail type-1 starts gspTask; 19FE4 clears 89C before type-2

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Competing hypotheses

- `H-RetailType1StartsSp`: viewer-window `0x80019D10` and
  `0x80019D58` are live (`$a0=0x800377C8` at 19D58);
  `0x80019D34` execs; type-2 still idle-starts (19DCC), so
  a clearer (`0x80019FE4` or equivalent) keeps 89C=0 for
  type-2.
- `H-RetailType1Absent`: `0x80019D10` is silent in the
  viewer window. Type-1 never runs, so 89C stays 0.
- `H-RetailType1BusySkip`: `0x80019D10` is live but
  `0x80019D78` is live and `0x80019D58` is 0 (does not
  start SP / does not write 89C).
- `H-RetailCoverageInvalid`: whole-RDRAM 10000-write
  control, viewer `0x800C28F0`, return `0x800C2E00`, or
  s3298's 19DCC idle pair miss.

## What ran

One independent retail Rice oracle, 25 s. Watches are
physical. Exec watches armed at first VI (no
`--pc-phase-log-width`). `--hit-cap 20000`. No `--press`.

```
tools/oracle/build/rs64_oracle
  --core .../libmupen64plus.dylib
  --rom  .../rogue_squadron.z64
  --video .../mupen64plus-video-rice.dylib
  --watch-write 0x0:0x800000
  --watch-pc 0x80019D10,0x80019D34,0x80019D58,0x80019D78,0x80019FE4,0x80019DCC,0x800C28F0,0x800C2E00
  --secs 25 --hit-cap 20000 --vi-trace --vi-poll
```

Capture: `scratch/agent/s3301_retail_type1_sp.log`.

No skip, allow, restore, wait bypass, or M5 Step 3.

`L_80019D10` is the type-1 idle-start path. `0x80019D34`
is `sb $s1, 0($s4)` with `$s4=0x8011A89C`. `0x80019D58`
is `osSpTaskLoad`. `L_80019D78` is the type-1 busy skip.
`0x80019FE4` is the 89C clearer (1:1 with 19ED0 on the
port). `L_80019DCC` is type-2 idle-start; `$v0` there is
the already-loaded `0x8011A89C`.

## Same-run positive controls

- whole-RDRAM write watch: 10000 hits; `[oracle]
  positive-control threshold reached`; watch index 1
  remained armed.
- `[gpr-ctl]` at 0.5 s (first VI 320).
- viewer entry `0x800C28F0` at 2.3 s (`prev_pc=0x800C5C98`,
  640 @ `0x0066aa00`).
- viewer return `0x800C2E00` at 6.5 s (`prev_pc=0x800C2DFC`,
  640 @ `0x0066aa00`, `$v0=1`).
- 19D10/19D34/19D58 and 19DCC live in the viewer window
  (242 / 242 / 242 / 258), width 640. Lifetime all printed
  (`--hit-cap 20000` not truncated: 15414 total hits).
- 1468 VI, 25.0 s wall / 24.5 s emulated. `rc=0`.

Title `1024 @ 0x00790400` did not fire: `[vi]` stays
`640` through 25.0 s (origins `0x00696100` / `0x00696600`
/ `0x0062c200` / `0x0062bd00`). Same Rice/25 s miss as
s3296–s3298. Failed instrument for the *viewer*
discriminator would have been a silent `0x800C2E00` or
silent 19D10/19DCC in 2.3–6.5 s. Both fired.

## Lifetime watches

| watch | hits |
|---|---:|
| write `[0x0,0x800000)` | 10000 (removed at 10000) |
| exec `0x80019D10` | 632, all `prev=0x80019CF0` |
| exec `0x80019D34` | 632, all `prev=0x80019D30`; `$s1=1`; `$v0=0x800377C8` |
| exec `0x80019D58` | 632, all `prev=0x80019D54`; `$a0=0x800377C8` |
| exec `0x80019D78` | **0** |
| exec `0x80019FE4` | 2074, all `prev=0x80019FE0`; `$a0=1` |
| exec `0x80019DCC` | 1442, all `prev=0x80019DA4`; `$v0=0` |
| viewer entry `0x800C28F0` | 1 |
| viewer return `0x800C2E00` | 1 |

19D10 = 19D34 = 19D58 (632). 19FE4 = 19D10 + 19DCC
(632 + 1442 = 2074). 19DCC `$v0 != 0` is 0/1442.
19D58 `$a0 != 0x800377C8` is 0/632. 19D10 `$a0` is
`0x80112AE0` n=3 then `0x80128CE0` n=629.

## Viewer window (2.3–6.5 s)

| site | n | notes |
|---|---:|---|
| 19D10 | 242 | all `prev=0x80019CF0`; `$v0=1` `$s1=1`; `$a0=0x80112AE0` n=1 then `0x80128CE0` n=241 |
| 19D34 | 242 | all `$s1=1` `$v0=0x800377C8` |
| 19D58 | 242 | all `$a0=0x800377C8` (`gspTask`) |
| 19D78 | 0 | type-1 never busy-skips |
| 19FE4 | 500 | 1:1 with 19D10+19DCC (242+258) |
| 19DCC | 258 | all `prev=0x80019DA4`; `$v0=0`; `$a0=0x80128C80` |

After every viewer 19D58, the next of {19FE4, 19DCC,
19D10} is 19FE4 (242/242). 241 of those then reach
19DCC with 19FE4 first; one is a second type-1
(`0x80112AE0` then `0x80128CE0`) before the next
19DCC. After every 19DCC, 19FE4 runs before the next
19D10 or 19DCC.

s3298's 19D90/19DCC idle pair is still live: 19DCC
`prev=0x80019DA4` and `$v0=0` for every hit (viewer
258 vs s3298's 259; lifetime 1442 vs 1447).

## Classification

- `H-RetailCoverageInvalid` is not selected for the
  viewer discriminator: rdram 10000, `[gpr-ctl]`,
  `0x800C28F0`, `0x800C2E00`, and in-window 19D10/19D58
  plus 19DCC all fired. Title 1024 is a post-viewer
  route-progress miss on this run.
- `H-RetailType1Absent` is refuted: 242 viewer 19D10
  from `0x80019CF0`, 241 with `$a0=0x80128CE0` (same
  type-1 message the port logs).
- `H-RetailType1BusySkip` is refuted: 19D78 exec=0;
  19D10=19D34=19D58 (632/632/632 lifetime, 242/242/242
  viewer).
- `H-RetailType1StartsSp` is selected: every type-1
  visit stores `$s1=1` at 19D34 and `osSpTaskLoad`s
  `gspTask` `0x800377C8` at 19D58. Type-2 still
  idle-starts because 19FE4 runs after every type-1
  (and every type-2) start and 19DCC always loads
  `0x8011A89C==0`. Combined with s3300, the port's
  type-1 start is the same; the extra `yieldw` is
  19FE4 not rerunning after 19ED0 is abandoned.

Single-source oracle evidence, compared with the s3300
port census (two-source for "both sides type-1-start
gspTask / write 89C; only retail keeps clearing"). No
audio or M5 Step 3 change.

Next discriminator: on the port, after last 19ED0
(`s2b0=2` takes `L_80019F50`), does `0x80019F6C`
(`sb $zero, 0($s2)`) clear 89F, and who writes
`0x8011A89F=1` before the first 19E80 fallthrough?
