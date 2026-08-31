# NEXT work unit — attribute retail title mode setup/apply ordering

HYPOTHESIS-ID: retail-title-transition-ordering

Session 3323 accepted every pre-swap width and still found no 640→1024 row
after `osViSwapBuffer` at `0x80035500`. The configured Windows/MIPS
PatchesLib host remains an external dependency.

## Competing hypotheses

- `H-ModeSetupBeforeApply`: a watched retail mode-setup call writes/returns a
  1024 template before the first title VI, and the apply path consumes it.
- `H-ApplyWithoutSetup`: the title transition is driven by an already-live
  1024 template; no mode setup call occurs in the target window.
- `H-OtherPublisher`: neither watched mode path attributes the transition,
  so publication is through another caller or an unobserved interrupt path.

## Discriminator

Add all candidate PCs to one oracle execution watch: `0x8001B6B0`
(`initVideoSubsystem`), `0x80018378` (`advanceVideoFrame`),
`0x80019914` (`applyPendingViChanges`), and `0x80035500`
(`osViSwapBuffer`). Phase-gate detailed rows at VI origin `0x00790400`,
width 1024, and run one Rice-backed 90-second capture with whole-RDRAM and
VI trace controls. Compare each candidate's execution time/GPR row with the
first title VI and record whether a 1024 mode template is written before the
transition. A setup→apply chain selects `H-ModeSetupBeforeApply`; title VI
with no setup execution selects `H-ApplyWithoutSetup`; neither watched path
selects `H-OtherPublisher`.

## Exact command

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle --core "$PWD/../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom "$PWD/../rogue_squadron64/rogue_squadron.z64" --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 90 --watch-write 0x0:0x800000 --watch-pc 0x8001B6B0,0x80018378,0x80019914,0x80035500 --pc-phase-log-width 0x00790400:1024 --vi-trace
```

No M5 Step 3 or port behavior change is authorized by this capture alone.
