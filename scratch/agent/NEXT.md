# NEXT work unit (s1095)

HYPOTHESIS-ID: retail-loop-pc-delay-classification

Run one established-schedule retail-oracle capture with execution watches on
`0x8006D9B0`, `0x8006D9B4`, and `0x8006D9BC`. Keep the whole-RDRAM, PIF, and VI
controls in the same run. This is one bounded runtime discriminator for the
static result that `9BC` is ordinary fall-through code.

Competing hypotheses:

* H-taken-branch: `9B4` fires, `9BC` stays zero, and the branch target/return
  path explains the missing fall-through instruction.
* H-fall-through: `9BC` fires after the compare, proving the retail path took
  the fall-through and that the earlier zero was a watch/callback anomaly.
* H-invalid-run: any positive control is absent, so the PC zeros cannot be
  interpreted.

Discriminator: positive whole-RDRAM callbacks, all eleven PIF Start presses,
and VI callback/poll agreement must all be present. With those controls,
`9B4>0` plus `9BC=0` selects H-taken-branch; `9BC>0` selects H-fall-through;
missing controls select H-invalid-run.

Exact command:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rsp /opt/homebrew/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --rom /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/rogue_squadron.z64 \
  --configdir scratch/agent/oracle_s1095_config --secs 120 --hold-ms 150 \
  --watch-write 0x0:0x800000 --hit-cap 10000 \
  --watch-pc 0x8006D9B0,0x8006D9B4,0x8006D9BC \
  --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' \
  --vi-trace --vi-poll --pif-trace \
  > scratch/agent/oracle_s1095.log 2>&1
```

Use the existing oracle binary and do not build the recomp for this static-
boundary follow-up. If the command is queued as a soak, the recipe must
watchdog and SIGKILL the process group.
