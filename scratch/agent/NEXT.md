# NEXT work unit (s2013) — repeat the retail status-value control

HYPOTHESIS-ID: m5-retail-status-poll-branch

## Work unit

Repeat the local retail-oracle status poll as a blocker-free M5 unit. The
phase-valid generated tree is still required for the port-side writer/thread
join, but it is not required to observe the retail status-value branch. Do not
rebuild or reconcile the generated/symbol trees for this unit.

## Discriminator and controls

Use the debugger-off `--status-poll --vi-poll` route described in
`tools/oracle/README.md`. The same run must reach VI 1024 and then hangar VI
512 at origins `0x006AB400`/`0x006AB800`; those are the positive phase controls.
Within that phase, slot 0 at physical `0x154620` must show the sequence
`0x00 → 0x01 → 0x02 → 0x03 → 0x00`. A missing `0x03` is a null only if the
phase controls pass. The poll does not attribute a host writer or thread.

The s2012 run already supplied this observation: slot 0 changed at 43.1s,
43.4s, 48.8s, and 48.8s while the run had reached VI 1024 at 17.3s and
hangar VI 512 at 38.4s. The static generated source independently maps the
table base to `0x80154620`, the stride to `0x1228`, and the seven candidate
writer PCs. Keep those two sources separate when classifying the value branch.

## Exact command

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --oracle-debugger 0 --oracle-emulator 1 --secs 60 --vi-poll --status-poll \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2013-retail-status-poll.log 2>&1
```

Do not turn this into a cross-run A/B on an animating scene. Do not infer the
port-side thread join from the poll, promote audio, alter status/spin/PI
behavior, or weaken a guard. The remaining port census stays open until the
phase-valid generated tree or owner authorization exists.
