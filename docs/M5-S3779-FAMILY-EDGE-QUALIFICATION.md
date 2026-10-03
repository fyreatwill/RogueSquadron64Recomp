# M5 s3779 family-edge qualification

The s3778 image-only capture was rebuilt with the existing regeneration-safe
s3769 family-entry transform enabled for the sentinel-protected generated
tree. The transform was made callable on an already-fixed-up tree through a
narrow `RS64_S3769_M5_FAMILY_ENTRY` dispatch; it remains part of
`fixup_game_funcs.py` and does not change game arguments or stores.

The Debug target built successfully. The image/oracle capture passed the
oracle whole-RDRAM positive control, all six family-store controls, title VI
1024 (`0x00790400`), and hangar VI 512 (`0x006AB400`). The image log contained
257 phase-qualified family-edge rows: S=128, I=1, and L=128. The edge control
fired for all three families. No edge row carried an argument in either
target buffer range; all 257 had `target_arg=0`. Family stores remained on
alternate objects. This is a qualified negative result for target-edge
presence, not an instrumentation null.

This selects `H-M5-RetailWriterFamilyAbsentTargetEdge` for the measured
target-edge class and refutes the missing-hook explanation. It does not prove
the alternate objects are illegitimate or identify the route/object decision
that prevents target-buffer arguments. No clear, store, audio gate, or game
value was changed.

Evidence: `scratch/agent/s3778_m5_family_edge/image.log` and the source/build
verification in the s3779 ledger entry.
