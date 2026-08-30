# NEXT work unit — retail: does the OSViMode table ever hold 1024?

HYPOTHESIS-ID: m5-osvimode-retail-1024-slot

Session 3278 selected `H-MissingTableRewrite` on the port: the four slots at
`0x80128D50+{0,0x50,0xA0,0xF0}` are 320 then 640, never 1024, while
`applyPendingViChanges` is live (`pending_mask9=0x1` at call 4) and publishes
the 640 slot `0x80128DF0`. The 320→640 rewrite is `initVideoSubsystem`'s
4×0x50 copy at `0x8001B6A8`. Iron rule 12: ask retail whether that table is
even the title-1024 publisher before instrumenting the stack-template builder.

## Competing hypotheses

- `H-RetailTableHas1024`: while title `1024 @ 0x00790400` is live, at least
  one of the four slot +8 words is stored as 1024. The port is missing that
  rewrite.
- `H-RetailTableNever1024`: title 1024 is reached and the whole-RDRAM
  control fires, but no 1024 store lands in those four +8 words. Title 1024
  is not published from this table.
- `H-RetailTableCoverageInvalid`: whole-RDRAM control or title 1024 gate
  missing; no slot conclusion.

## Discriminator

One retail oracle run. Watch the four physical width words and record
post-store values phase-gated to title 1024 and pre-title 640. A 1024
post-value at title selects `H-RetailTableHas1024`. Title 1024 with no 1024
post-value on any of the four words selects `H-RetailTableNever1024`.

Positive control: `--watch-write 0x0:0x800000` must hit (cap 10000 is fine)
AND `--vi-trace` must show title `1024 @ 0x00790400`. A silent whole-RDRAM
watch is a failed instrument, not an empty table.

## Exact command

From the repository root:

```sh
tools/oracle/build/rs64_oracle \
  --core ~/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom  ~/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 60 --hit-cap 10000 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x128D58:0x128D5C \
  --watch-write 0x128DA8:0x128DAC \
  --watch-write 0x128DF8:0x128DFC \
  --watch-write 0x128E48:0x128E4C \
  --post-value-watch 1 --post-value-watch 2 \
  --post-value-watch 3 --post-value-watch 4 \
  --pc-hist-phase 0x0066A500:640 \
  --pc-hist-phase 0x00790400:1024 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --vi-trace --vi-poll \
  > scratch/agent/s3279_retail_osvimode_slots.log 2>&1
```

Watches are physical. Slot +8 words are `0x80128D50+i*0x50+8`. Do not change
audio behavior. Do not run M5 Step 3. Do not repeat the local missing-target
`PatchesLib` build.
