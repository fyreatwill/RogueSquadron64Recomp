# NEXT work unit — attribute retail game-side 1024 mode request

HYPOTHESIS-ID: m5-vi-mode-stall

## Single work unit

Run one retail-grounded oracle capture that watches `osViSetMode`
(`0x800352D0`) and the surrounding VI context path, with the whole-RDRAM
positive control, Rice video, and the validated Start schedule. Use the
`exec-prev` histogram for the 1024 request to identify the game-side jal site.
Then map that site to the retail symbol/decomp and the corresponding port
function. Do not modify behavior or add a port instrument in this unit.

## Competing hypotheses

- H-RequestMissing: the retail 1024 request's game-side jal site has no
  corresponding port execution before VI-640.
- H-RequestAliased: the corresponding port path executes but resolves through
  the wrong overlay/generated function.
- H-RequestDescriptor: the corresponding port path executes and submits a
  descriptor, but its width differs from retail's legitimate 1024 descriptor.

## Discriminating measurement

The oracle's `exec-prev` row for the retail width-1024 `osViSetMode` execution
must identify the jal site. If that site has no corresponding port execution,
H-RequestMissing wins; if it executes through a different generated body,
H-RequestAliased wins; if it executes and submits a non-1024 mode,
H-RequestDescriptor wins. A consumer PC or symbol identity alone cannot select
one of these.

## Exact commands

1. `tools/oracle/build/rs64_oracle --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom "$HOME/Documents/Tools/rogue_squadron64/rogue_squadron.z64" --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --watch-write 0x0:0x800000 --watch-pc 0x800352D0,0x80035550 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`
2. Grep the captured output for the 1024 `osViSetMode` execution and its
   `exec-prev` histogram; map the identified jal site with bounded `rg`/`sed`
   windows in the retail symbol/decomp and port generated files.
3. Record the classification and evidence in
   `scratch/agent/s3058_m5_vi_request_attribution/AUDIT.md`.
