# NEXT work unit (s1871)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F1FF4` (`0x800F1FF4`,
size `0x7C`). s1870 synchronized leftover `func_800F1E7C` to
`initActorRenderDescriptorIfUninit` (`0x800F1E7C`, `0x178`, H2).
Last-15 after s1870 still include s1856's M4 REVISIT, so this
is not another REVISIT. Do not re-confirm
`initActorRenderDescriptorIfUninit` or re-run the `0x8000` Y
census.

Competing hypotheses:

- H1 already-named: companion `mission_overlay.txt`, generated
  headers/body/INL, and TOML already agree on
  `initActorRenderDescriptorWithNpcVelocity` at `0x800F1FF4`
  size `0x7C`. Confirm and advance the cursor.
- H2 rename: at least one of TOML / generated / companion still
  carries `func_800F1FF4` or a stale name; synchronize to the
  companion sequential listing.
- H3 leave leftover: the `0x7C` span has no recoverable
  semantics; leave the placeholder and move on.

Exact commands:

```
# Companion, generated, TOML, and the 0x7C body at 0x800F1FF4.
# Neighbor leftover after the already-named health family is
# func_800F2208 (0x800F2208, 0x108).
# 4 generated jal 0x800F1FF4 sites (funcs_37.c + funcs_38.c
# already initActorRenderDescriptorWithNpcVelocity).
# First insn addiu $sp, $sp, -0x30; last jr $ra / addiu $sp, $sp, 0x30
# at 0x800F2068 / 0x800F206C. Next already-named occupant is
# setNpcHealth at 0x800F2070.
```

Expected splits:

- H1: all three sources already name the same symbol; no rename
  diff; cursor advances.
- H2: a real rename lands in TOML and/or generated fixup
  (peek: TOML is still `func_800F1FF4`; companion/generated
  already `initActorRenderDescriptorWithNpcVelocity`).
- H3: document why the span is unnameable; cursor advances.

Parked (not this iteration): hangar/512 check of live `0x8000` Y
(s1856 window was attribution 640 only).
