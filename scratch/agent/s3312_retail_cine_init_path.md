# Session 3312 — retail jal 0x800A62B4 takes the flag-byte path

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

## Competing hypotheses

- `H-RetailTimeBypass`: 626C stays `taken=0` until ~48 s, then
  `taken=1` (count >= limit-10), 6274 silent on that window,
  6288 not taken, 62B4 fires.
- `H-RetailFlagSet`: 6274 `taken=0` (`$a0!=0`) before the
  time threshold, then 62B4 fires.
- `H-RetailJalOther`: 62B4 fires without 626C/6274/6288
  describing the path.
- `H-CoverageInvalid`: missing 10000-write, `[gpr-ctl]`, VI
  `640 @ 0x0066A500`, cinematic entry, or 62B4.

## What ran

One independent retail Rice oracle. Watches are physical. No
`--press`. No port instrumentation or build. No M5 Step 3.

`print_gpr_fields` now includes `$v1` so 626C taken is direct.
Whole-RDRAM write watch is the positive control. Detail-watch
on 626C/6274/6288/62B4/AF4B8.

Driver: `scratch/agent/s3312_retail_cine_init_path/run.sh`.

```
tools/oracle/build/rs64_oracle
  --core .../libmupen64plus.dylib
  --rom  .../rogue_squadron.z64
  --video .../mupen64plus-video-rice.dylib
  --watch-write 0x0:0x800000
  --watch-pc 0x800A5D80,0x800A626C,0x800A6274,0x800A6288,0x800A62B4,0x800AF4B8
  --detail-watch 2,3,4,5,6
  --secs 90 --hit-cap 20000 --vi-trace --vi-poll
```

MIPS: `0x800A626C` `beq $v1,$zero → 627C` (taken bypasses the
flag). `0x800A6274` `beq $v0,$zero → 62EC` on skip-allow
`$a0` (taken skips the jal). Skip-allow is 1 if incoming `$a0`
is set (`getControllerNewButtonsPressed` `& 0x9000` at
`0x800A6208`) else `lbu 0x800B0B1C` at `0x800A6244`. Prologue
`sb $zero, 0xB1C($v0)` at `0x800A5EE8` zeros that byte.

## Same-run positive controls (90 s)

- Whole-RDRAM write watch: 10000 hits; positive-control threshold
  reached.
- `[gpr-ctl]` present. `$v1` printed on 2406 exec rows.
- VI `320 → 640 @ 0x0066A500` at 2.2 s.
- Cinematic entry `0x800A5D80` at 6.6 s (`prev=0x8003E10C`,
  `$a0=0x13`). Second entry at 80.5 s (`prev=0x8003E324`).
- 62B4 n=1 at 48.1 s. AF4B8 n=1 stores `$v0=0x800D9780`.
- Title `1024 @ 0x00790400` at 49.2 s.
- 5366 VI, 90.0 s wall / 89.4 s emulated. `rc=0`.

## Path table

| site | n / printed | GPRs | taken |
|---|---|---|---|
| time-pred `0x800A626C` | 1190 / 1189 | `$v1=1` all; `$v0=0x4A6` first attract | **0** all |
| flag-byte `0x800A6274` | 1190 / 1190 | `$a0=0` then `$a0=1` at 48.1 s | 1167 then **0** |
| already-active `0x800A6288` | 23 / 23 | first `$v0=0`; then 22 `$v0=1` | first **0**, then 1 |
| init-jal `0x800A62B4` | 1 / 1 | `prev=0x800A62B0` | fires 48.1 s |
| init-sw `0x800AF4B8` | 1 / 1 | `$v0=0x800D9780` | 48.1 s |

First-attract flag: 975 visits `$a0=0` `taken=1` (10.5–48.1 s),
then `$a0=1` `taken=0` at 48.1 s (23 visits through 48.8 s).
Last 626C before the jal: `$v1=1` `$a0=1` `taken=0`. First
6288: `$v0=0` `$a0=1` `taken=0` then the jal; subsequent 6288
skip because the pointer is live.

## Conclusion

`H-RetailFlagSet` is selected. `H-RetailTimeBypass` is refuted
(626C `$v1=1` on every printed row; count never reaches
limit-10). `H-RetailJalOther` is refuted (`prev=0x800A62B0`).
`H-CoverageInvalid` is refuted.

Combined with port Session 3311, both sides leave 626C
not-taken. The port-only stop is skip-allow `$a0` staying 0,
not a too-slow loop missing the 1190 count bypass. `$a0` is
the OR of incoming Start/A new-press and `0x800B0B1C`.

No M5 Step 3. Next discriminator: independent retail who
sets skip-allow at 48.1 s (incoming `$a0` at `0x800A6238`
versus a write of physical `0x000B0B1C`).

Evidence dir: `scratch/agent/s3312_retail_cine_init_path/`.
