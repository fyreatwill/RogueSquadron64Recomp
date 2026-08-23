# NEXT work unit (s2178) — retail word bits at extract $a1+0x20 / first-cross $a2+8

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2177 selected `H-RetailExecsJal8640`: retail executes
`0x800A8640` n=6183 at cinematic 640/`0x00696100`,
transfers to `extractOrthonormalFrameFromStruct`, and
`vec3Cross` `0x80019548` n=32795. Dest `$a0=0x80165E40`
10/10 logged. Oracle did not print `$a1` or memory
words, so no NaN/finite claim.

Ask ground truth before any port instrument or
`NAN_CHECK` change: is the word retail loads as
`NAN_CHECK` f10 finite or NaN?

That word is dest+0x14 = source `$a1+0x20` (extract
`0x80059D48` `lwc1 0x20($a1)` / first orthonormalize
cross `$a2=dest+0xC`, `$a2+8`).

Do not S32-address, NULL-skip, re-flip default-on,
skip/allow the lwc / transform / extract jal, disable
`NAN_CHECK`, or add a wait/slot guard.

## Competing hypotheses and discriminator

IEEE single: NaN iff `(w & 0x7F800000)==0x7F800000 && (w & 0x007FFFFF)!=0`.
Join first-cross rows on prev=`0x80059F3C` at 640 cinematic.

- `H-RetailSourceWordFinite`: same-run `[gpr-ctl]`,
  watch0 10000, VI 640 including `0x00696100`; logged
  cinematic first-cross `w_a2p8` (and extract
  `w_a1p20`) are finite (not NaN).
- `H-RetailSourceWordNaN`: those controls fire; logged
  cinematic first-cross `w_a2p8` (or extract `w_a1p20`)
  is NaN bits (retail has no `NAN_CHECK`).
- `H-CoverageFailure`: missing `[gpr-ctl]`, watch0
  10000, VI 640/`0x00696100`, or zero printed
  `w_a2p8`/`w_a1p20` at those PCs.

Positive controls: `[gpr-ctl]`; watch 0 write
callbacks=10000; `[vi]` 640 origin `0x00696100`;
printed `a1=` field on an EXEC hit.

## Exact commands

Oracle rebuild only (no game rebuild). In
`tools/oracle/rs64_oracle.c` `print_gpr_fields`, also
print `a1=gpr32(5)` and `s0=gpr32(16)`. On EXEC detail
print: if `pc==0x80019548` print
`w_a2p8=pDebugMemRead32(debug_rdram_addr((gpr32(6)+8)&~3u))`;
if `pc==0x80059D48` print
`w_a1p20=pDebugMemRead32(debug_rdram_addr((gpr32(5)+0x20)&~3u))`.
Then `tools/oracle/build.sh` (no core rebuild).

    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 45 --hit-cap 64 \
      --watch-write 0x0:0x800000 \
      --watch-pc 0x800A8640,0x80059D18,0x80059D48,0x80059F3C,0x80019548 \
      --first-watch 0 --vi-trace \
      > scratch/agent/oracle_s2178_vec3_word.log 2>&1

Table to `scratch/agent/s2178_vec3_word.txt`.
Classify each logged `w_a2p8` with prev=`0x80059F3C`
and each `w_a1p20` as finite / Inf / NaN. Also record
`$a1` at `0x800A8640` / `0x80059D18`.
