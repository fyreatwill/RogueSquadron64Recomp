# NEXT work unit — which submitGfxFrame jal stalls on invocation 3

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3289 selected `H-StuckAfterFallthrough` (`submitGfxFrame`
`0x8000C07C`): after `2D50` n=3 fallthrough, `SENT` n=3 fired and
`SRET` n=3 did not. The other five fallthrough callees returned.
`29E0` n=4 silent. Controls (viewer entry, 640 / `0x0066A500`,
`2D50` n=3 taken=0) passed. This is the third *viewer-loop
invocation* of that jal, not the disproven internal "iter 3 hangs"
reading of `func_8000C07C`.

Keep s3288 fade and s3289 `SENT`/`SRET` in the same build.

## Competing hypotheses

- `H-SubmitRecvBlocked`: on `SENT` n=3, one of the three
  `osRecvMesg` jals (`0x8000C0B4`, `0x8000C2B8`, `0x8000C4B0`) is
  entered and does not return.
- `H-SubmitYieldBlocked`: on `SENT` n=3, `yieldFromSpThread`
  (`0x8000C0BC`) or `yieldFromGfxFrame` (`0x8000C2C0` /
  `0x8000C4B8`) is entered and does not return.
- `H-SubmitOtherCallee`: on `SENT` n=3, a non-recv/yield jal
  (including `osSendMesg` `0x8000C2A0`) is the last site and does
  not return.
- `H-SubmitCoverageInvalid`: `SENT` n=3 silent, or `SRET` n=3
  fires (s3289 stale), or viewer/640/`2D50` n=3 controls miss.

## Discriminator

One Debug rebuild with a fixup probe at every jal *entry* inside
`submitGfxFrame` (23 sites in `funcs_3.c`) plus *return* of the
seven recv/yield/send sites. Keep `[s3288-fade]` and `[s3289-stall]`
`SENT`/`SRET`. Rate-limit first 10 + every 50; always print the
first return-miss. One 30 s port run from `build/` with the ROM
present. Positive control: s2045 `[m5-postwait]` viewer `entry`
AND `[phase]` 640 at `0x0066A500` AND `[s3288-fade] site=2D50 n=3
taken=0` AND `[s3289-stall] site=SENT n=3` without `SRET` n=3.

Last open recv site on `SENT` n=3 selects `H-SubmitRecvBlocked`.
Last open yield site selects `H-SubmitYieldBlocked`. Last open
other jal selects `H-SubmitOtherCallee`. `SRET` n=3 or silent
controls are a failed instrument.

Do not add a skip, allow, restore, or wait bypass. No M5 Step 3.

## Exact commands

```sh
python3 tools/apply_s3290_submit_gfx_stall.py
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
```

Then from `build/`, 30 s, SIGKILL, `ROGUESQ_LOG_M5_POSTWAIT=1` plus
existing `[phase]` / `[slot-ret-caller]` (unconditional). Log:
`scratch/agent/s3290_submit_gfx_stall.log`.
