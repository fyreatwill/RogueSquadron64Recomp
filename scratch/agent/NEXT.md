# NEXT work unit — port: after last 19ED0, does 19F6C clear 89F?

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3301 selected `H-RetailType1StartsSp`: viewer
type-1 starts `gspTask` `0x800377C8` and writes 89C;
19FE4 is 1:1 with every type-1 and type-2 start, so
19DCC always loads `0x8011A89C==0`. Combined with s3300,
the port's type-1 start is the same; the extra yield is
19FE4 not rerunning after 19ED0 is abandoned.

Last 19ED0 on the port has `s2b0=2`, so `bne` at
`0x80019ED4` takes `L_80019F50` (not 19F1C). That path
ends at `0x80019F6C` `sb $zero, 0($s2)` which should
clear `0x8011A89F`. Session 3295 then sees 19E80
fallthrough (`$s2[0]==1`). Named 1-store is `0x80019E70`
(`sb $s1, -0x5761($at)` = 89F, `$s1=1`) on the
yield-complete arm; `0x80019E60` stores 0 when yield
status is 0.

## Competing hypotheses

- `H-Ed0NonzeroNoClear`: last 19ED0 takes 19F50 / 19F64
  returns, but 19F6C is silent, so 89F is never cleared
  on that visit.
- `H-Ed0ClearsThenE70`: 19F6C runs (89F=0), then 19E70
  stores 1 before the first 19E80 fallthrough.
- `H-Ed0ClearsThenOther`: 19F6C runs, 19E70 is silent in
  that gap, some other PC writes 89F=1.
- `H-CoverageInvalid`: viewer `[m5-postwait]` entry,
  `[phase]` `640 @ 0x0066A500`, SENT n=3, last 19ED0,
  19F64, first 19E80F, or the new probes miss at width
  640.

## Discriminator

One 30 s port run. 19F6C silent after last 19ED0 selects
`H-Ed0NonzeroNoClear`. 19F6C live then 19E70 before first
19E80F selects `H-Ed0ClearsThenE70`. 19F6C live, 19E70
silent in the gap, 19E80F still `$s2[0]==1` selects
`H-Ed0ClearsThenOther`. Missed controls is a failed
instrument.

Do not add a skip, allow, restore, or wait bypass. No M5
Step 3.

## Exact commands

Write `tools/apply_s3302_89f_clear.py` (and hook the same
transform from `fixup_game_funcs.py`) probing `L_80019F50`,
`0x80019F6C`, `0x80019E60`, `0x80019E70`. Keep s3288 fade /
s3289 SENT / s3290 inner / s3293 gate / s3294 loop /
s3295 dispatch / s3299 type-2 / s3300 89C. Print
`$s2[0]`, 89C, 89F, yieldw.

```
python3 tools/apply_s3302_89f_clear.py
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
  cmake --build build --config Debug --target RogueSquadron64Recomp
# from build/, ROM present, 30 s then SIGKILL:
env ROGUESQ_LOG_M5_POSTWAIT=1 ./RogueSquadron64Recomp
```

Log: `scratch/agent/s3302_port_89f_clear.md` plus the
captured run log.
