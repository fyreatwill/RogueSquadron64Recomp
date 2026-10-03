# M5 s3778 — clear-edge witness repaired

The caller-side writer witness at `0x8008F2CC` was moved past the MIPS delay
slot at `0x8008F2D0`. The old placement sampled `$a2` before the delay-slot
assignment and therefore reported `a2=0`. The fix is regeneration-safe in
`tools/apply_s3423_m5_writer_setup.py`.

The Debug build completed. The prescribed image-only capture ran beside the
retail oracle: the oracle whole-RDRAM positive control fired; the image arm
passed six family-store controls and reached title `0x00790400` and hangar
`0x006AB400` without a crash marker.

The corrected target-phase row was:

```text
edge=0x8008F2CC a0=0x801797B0 a2=0x298 clear_obj=0x801797B0 alloc_len=0x298
```

This validates the clear-object witness and rules out the stale-register
explanation. Family stores still targeted alternate objects (for example
`0x80165E98`), and no family-edge row or edge control was emitted. The clear
object is therefore not yet joined to the family-store route; no mitigation is
authorized.
