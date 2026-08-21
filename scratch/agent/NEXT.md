# NEXT work unit (s2168) — retail $a0/$v0 at matchKeywordWithPriority

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2167 selected `H-PortStoreMatchesRetail`. Table:
`scratch/agent/s2167_port_store_ab.txt`.

The port writes and reloads retail's heap pointer
`0x8025A580` at dest `0x800C7B0C`. Image-arm SIGBUS is
later: `matchKeywordWithPriority+88`, `si_addr=0x380000030`
(`rdram+0x80000030`), last-guest-pc `0x8000834c`. Guest
body starts at `0x800AF2C8`:

    lw  $v0, 0x0($a0)
    lw  $t0, 0x30($v0)    /* host +88 class: unsigned 0x80000030 */

Ask retail whether that path executes at cinematic 640
`0x00696100` and what `$a0`/`$v0` are. Do not S32-address,
NULL-skip, re-flip default-on, or add a wait/slot guard.

## Competing hypotheses and discriminator

- `H-RetailAlsoWildV0`: `0x800AF2CC` executes at 640
  `0x00696100` with `$v0` 0 or `0x80000000` (or otherwise
  not KSEG0 RDRAM `0x80000000..0x803FFFFF`). Port crash
  matches a retail-wild object header.
- `H-RetailValidV0`: `0x800AF2CC` executes there with `$v0`
  in KSEG0 RDRAM and not `0x80000000`. Port `$v0` is the
  defect; retail takes a legitimate `0x30($v0)`.
- `H-RetailNeverExec`: lifetime exec at `0x800AF2C8`/`CC`/`D0`
  is 0 after watch-0 removal while VI 640/`0x00696100` is in
  the same log. This is not the cinematic path.
- `H-CoverageFailure`: no `[gpr-ctl]`, watch-0 callbacks !=
  10000, or the run never reaches VI 640 / `0x00696100`.

Positive control: `[gpr-ctl]` plus watch 0 write
callbacks=10000 and a VI 640 origin `0x00696100` row in the
same log.

`--watch-pc` prints `$v0/$s1/$a0/$a2`. Discriminator is
`$v0` at `0x800AF2CC` (post-`lw $v0,0($a0)`). `$a0` at
`0x800AF2C8` is the producer.

## Exact commands

No game rebuild. Oracle only:

    tools/oracle/build/rs64_oracle \
      --core "$(pwd)/tools/oracle/mupen64plus/libmupen64plus.dylib" \
      --rom "$(pwd)/rogue_squadron.z64" \
      --video "$(pwd)/tools/oracle/mupen64plus/mupen64plus-video-rice.dylib" \
      --secs 45 --hit-cap 64 \
      --watch-write 0x0:0x800000 \
      --watch-pc 0x800AF2C8,0x800AF2CC,0x800AF2D0 \
      --first-watch 0 --vi-trace \
      > scratch/agent/oracle_s2168_match_keyword.log 2>&1

If the binary/plugin paths differ, copy the s2166 command
from `scratch/s73_post_a_scene/s2166_cutscene_a2_50_writer.txt`
and only change `--watch-pc` and the log path.

Do not flip `get_rsp_microcode`. Do not skip/allow/guard
`matchKeywordWithPriority`.
