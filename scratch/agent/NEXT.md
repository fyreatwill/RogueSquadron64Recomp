# NEXT work unit (s2169) — port $a0/$v0 at matchKeywordWithPriority

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2168 selected `H-RetailValidV0`. Table:
`scratch/s73_post_a_scene/s2168_match_keyword_oracle.txt`.

Retail executes `matchKeywordWithPriority` at cinematic 640
with `$a0=0x802231EC` (heap) and post-`lw` `$v0=0x800CDB58`
(KSEG0 object, not `0x80000000`). Caller is always
`spawnCutsceneEffectsAndCues` `0x800A9248`:

    0x800A9244  lw  $a0, 0x50($v0)
    0x800A9248  jal matchKeywordWithPriority
    0x800AF2C8  lw  $v0, 0x0($a0)
    0x800AF2CC  lw  $t0, 0x30($v0)   /* port SIGBUS: $v0=0x80000000 */

That caller +0x50 is a *different* word than dest
`0x800C7B0C` (closed by s2167). Ask the port, same-build
`ROGUESQ_AUDIO_UCODE=1` vs `=0`, what `$a0` and `$v0` are
at those PCs in the 640 cinematic. Do not S32-address,
NULL-skip, re-flip default-on, skip/allow the function, or
add a wait/slot guard.

## Competing hypotheses and discriminator

- `H-PortA0Wild`: image-arm `$a0` at `0x800A9244` /
  `0x800AF2C8` is 0, `0x80000000`, or not KSEG0 RDRAM;
  stub `$a0` is retail-class heap. The caller +0x50 load
  is the split.
- `H-PortA0OkV0Wild`: both arms have retail-class `$a0`
  (heap `0x8022xxxx`); image-arm word at `0($a0)` / `$v0`
  at `0x800AF2CC` is 0 or `0x80000000`; stub `$v0` is
  `0x800CDB58`-class. The header word is the split.
- `H-PortMatchesRetailUntilLater`: both arms match retail
  (`$a0` heap, `$v0` KSEG0 not base) on every logged 640
  call, including the last row before SIGBUS. Then the
  `si_addr=0x380000030` attribution is wrong or a later
  instruction. Unlikely given host +88 = `MEM_W($v0,0x30)`.
- `H-CoverageFailure`: `[match-kw-ctl]` never fires at
  640, or `=1` dies before the first call.

Positive control: `[match-kw-ctl]` at width=640 (include
origin `0x00696100` if present) on **both** arms, plus
the `=0` arm reaching title.

Discriminator is `$a0` at `0x800AF2C8` and `$v0` at
`0x800AF2CC` on the image-arm crashing call vs stub.

## Exact commands

Diagnostic only. Clone the s2167 dual-edit (live generated
C + `../N64Recomp/fixup_game_funcs.py`) so the probe
survives regen. Probe sites:

1. `funcs_27.c` after `0x800A9244` `lw $a0, 0x50($v0)`:
   log caller `$v0` base, dest `base+0x50`, loaded `$a0`.
2. `funcs_29.c` `matchKeywordWithPriority` after
   `ctx->r2 = MEM_W(ctx->r4, 0X0)` and **before**
   `MEM_W(ctx->r2, 0X30)`: log `$a0` and post-lw `$v0`.
   Rate-limit first 20 then every 50; always log when
   `$v0` is 0 or `0x80000000`. Env
   `ROGUESQ_LOG_MATCH_KW` (also `ROGUESQ_LOG_ALL`).

Then cmake only (no full regen if the live files were
patched in lockstep with fixup):

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
      cmake --build build --target RogueSquadron64Recomp

Same-build concurrent 90s SIGKILL arms, recipe as s2167:

    GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_MATCH_KW=1' \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2169_on 30 12
    GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_MATCH_KW=1' \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2169_off 30 12

Watchdog SIGKILL at 90s. Table to
`scratch/s73_post_a_scene/s2169_match_kw_ab.txt`.

Do not flip `get_rsp_microcode`. Do not skip/allow/guard
`matchKeywordWithPriority`.
