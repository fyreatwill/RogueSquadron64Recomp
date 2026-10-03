# Next work unit: M5 family destination provenance versus route identity

HYPOTHESIS-ID: m5-retail-writer-port-edge

Use s3769's boundary: in both port arms, `rs_strncpy` and
`loadTextureToMemory` entered in title and hangar but no argument was in the
target ranges; `initTextureLUTAndAllocBuffers` had no target-phase entry. The
next census must observe internal store destinations, not only entry
arguments, and must retain the independent controls.

Competing hypotheses:

- `H-M5-FamilyStoresAlternateLegitimateObject`: S/L internal stores land in
  a legitimate alternate texture/source object, while I is setup-only or
  legitimately pre-target.
- `H-M5-FamilyStoresExpectedTargetViaHiddenPointer`: one or more family bodies
  derive the target buffer internally despite non-target entry arguments.
- `H-M5-FamilyRouteIdentityMismatch`: family-derived destinations disagree
  with the clear-associated route object, identifying an object/route join
  mismatch rather than absent execution.

Discriminator: one phase-gated, regeneration-safe store census for every
internal store site in the three family bodies, recording family, store PC,
effective destination, value/width, phase, route ordinal, and relation to the
title (`0x178C80..0x178F80`) or hangar (`0x1797B0..0x179A48`) target ranges.
The oracle must retain whole-RDRAM, title, and hangar controls. Both image and
silent port arms must reach both target VIs; otherwise that arm is invalid.

Before building, locate all family-body stores and the existing fixup anchors:

`rg -n -C 2 'rs_strncpy|initTextureLUTAndAllocBuffers|loadTextureToMemory|MEM_[BHW]|80007670|8001E2C0|8001FA|8001FB|8001FD' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_{2,6}.c`

`rg -n 's3769 M5 family entry edges|rs64_m5_family_entry|rs64_m5_writer_parity' /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`

Use one fixup-script batch, one Debug build, and one concurrent oracle/image/
silent run. Do not suppress the clear, inject payloads, or change an audio
gate.
