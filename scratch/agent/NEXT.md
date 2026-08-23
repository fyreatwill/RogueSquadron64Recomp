# NEXT work unit (s2200) — obtain retail target-phase VI field ground truth

HYPOTHESIS-ID: m5-a1-vi-field-alternation

## Work unit

Run one driven retail-oracle session with Rice, a whole-RDRAM positive-control
watch, `--vi-trace`, and an execution watch on retail
`osViGetCurrentField` (`0x80034D90`). Keep the existing target-origin route
schedule and collect the field return value together with the VI width/origin
printed on every execution row. Do not build the port or flip the diagnostic
knob; this is the independent ground-truth step selected by s2199.

## Competing hypotheses and discriminator

- H-RetailFieldAlternates: at width 640 and origins `0x00696100`/
  `0x00696600`, retail `osViGetCurrentField` returns both 0 and 1, selecting
  the port field alternation as the correct missing transition.
- H-RetailField0Target: retail returns only 0 at both target origins, so the
  port's alternating field is a route-recovery artifact and the target
  transition is elsewhere.
- H-RetailFieldWatchCoverage: the whole-RDRAM control fires but the driven
  run does not reach both target origins or the execution watch does not fire
  in the target phase; reject the null and redesign the oracle arm.

The discriminator is the target-phase matrix
`(VI origin, osViGetCurrentField v0)` from one oracle run. Accept a conclusion
only if the whole-RDRAM watch is positive and `--vi-trace` shows repeated 640
rows at both target origins. The existing source-level result remains
single-source until this matrix is collected.

## Exact command

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom ./rogue_squadron.z64 \
  --video /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --rsp /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --secs 45 --watch-write 0x0:0x800000 --watch-pc 0x80034D90 \
  --hit-cap 10000 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start \
  --hold-ms 150 > scratch/agent/s2200_retail_vi_field_target.log 2>&1
```

Do not add a port guard, mitigation, task rewrite, or audio default change.
