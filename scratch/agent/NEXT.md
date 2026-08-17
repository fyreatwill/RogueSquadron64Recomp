# NEXT work unit (s1870)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F1E7C` (`0x800F1E7C`,
size `0x178`). s1869 synchronized leftover `func_800F1B40` to
`raycastTerrainAndNpcs` (`0x800F1B40`, `0x33C`, H2). Last-15
after s1869 still include s1856's M4 REVISIT, so this is not
another REVISIT. Do not re-confirm `raycastTerrainAndNpcs` or
re-run the `0x8000` Y census.

Competing hypotheses:

- H1 already-named: companion `mission_overlay.txt`, generated
  headers/body/INL, and TOML already agree on
  `initActorRenderDescriptorIfUninit` at `0x800F1E7C` size `0x178`.
  Confirm and advance the cursor.
- H2 rename: at least one of TOML / generated / companion still
  carries `func_800F1E7C` or a stale name; synchronize to the
  companion sequential listing.
- H3 leave leftover: the `0x178` span has no recoverable
  semantics; leave the placeholder and move on.

Exact commands:

```
# Companion, generated, TOML, and the 0x178 body at 0x800F1E7C.
# Neighbor leftover after this one is func_800F1FF4 (0x800F1FF4,
# 0x7C; companion/generated initActorRenderDescriptorWithNpcVelocity;
# TOML leftover).
# 18 generated jal 0x800F1E7C sites (funcs_36/37/38/39.c already
# initActorRenderDescriptorIfUninit; funcs_18.c + funcs_19.c still
# LOOKUP_FUNC(0x800F1E7C)). Companion undefined_funcs_auto.txt still
# lists leftover func_800F1E7C.
# First insn addiu $sp, $sp, -0x30; last jr $ra / addiu $sp, $sp, 0x30
# at 0x800F1FEC / 0x800F1FF0.
```

Expected splits:

- H1: all three sources already name the same symbol; no rename
  diff; cursor advances.
- H2: a real rename lands in TOML and/or generated fixup
  (peek: TOML is still `func_800F1E7C`; companion/generated
  already `initActorRenderDescriptorIfUninit`).
- H3: document why the span is unnameable; cursor advances.

Parked (not this iteration): hangar/512 check of live `0x8000` Y
(s1856 window was attribution 640 only).
