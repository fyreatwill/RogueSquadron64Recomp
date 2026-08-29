# NEXT work unit — M3 voice-slot producer idiom audit

HYPOTHESIS-ID: m3-musyx-voice-slot-producer-contract

## Single work unit

Audit every producer and consumer edge in the existing inventory for the
voice-slot initialization idiom centered on `musyxInitVoiceFromSample`
(`0x80092128`). This is a complete source audit, not a single-site guard
change. M5 Step 1 remains blocked at VI 640 until a route change supplies
title/hangar controls.

Competing hypotheses and the discriminating measurement:

- `H-LegitimateWriter`: every voice-slot base/index/value reaching the audited
  writes is produced by a bounded, initialized game path; existing guards are
  defensive only and no new mitigation is justified.
- `H-BadProducer`: at least one reachable writer can produce an invalid base or
  index before the consumer; identify that writer and its ordering edge as the
  engineering target.
- `H-UnreachableGuard`: the suspicious path is not callable in the current
  image, and the apparent defect is generated/runtime-only; record it without
  changing behavior.

The discriminator is one whole-class census of all callers, all writes to the
voice base/index fields, and all guard sites, joined by guest PC and field
offset. `H-LegitimateWriter` requires a bounded writer for every observed
edge; `H-BadProducer` requires a concrete writer that emits the bad value
before the consumer; `H-UnreachableGuard` requires no callable edge in the
retail-grounded inventory. A null is invalid unless the census positive
control marks every known writer and caller.

Exact commands:

```sh
rg -n 'musyxInitVoiceFromSample|audio-voice-baseptr-guard|avf-gate|voice' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_26.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
rg -n '0x80092128|musyxInitVoiceFromSample|voice.*base|voice.*slot|0x8014' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/src \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/docs/mips_to_c 2>/dev/null
rg -n 'audio-voice-baseptr-guard|avf-gate|voice-array|voice.*writer' \
  docs scratch/agent | head -200
```

Expected outcome: produce one complete writer/consumer table and either prove
the existing contract, name one legitimate bad producer with its ordering
edge, or prove the path is unreachable. Do not add a guard or build/run until
the table selects one of those outcomes.
