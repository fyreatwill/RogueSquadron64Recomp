# Session 5571 — `fake_func_800027B8` exact-span audit

## Competing hypotheses

- H1: this is a callable generated function with an independently supported semantic name.
- H2: this is a data or instruction fragment and should use a mechanical gap name.
- H3: the generated and mapping surfaces are already synchronized, or the address is not a live callable record.

## Discriminator and result

The generated body, companion symbol file, and checked-in symbols table were
compared at the exact address and successor boundary.

- `../N64Recomp/RecompiledFuncs/funcs_0.c` emits `fake_func_800027B8` as
  exactly two `addu` instructions at `0x800027B8` and `0x800027BC`, followed
  by `processPolledControllerData` at `0x800027C0`. It has no prologue,
  return, or independent callable body.
- `../rogue_squadron64/symbol_files/main_overlay.txt` retains the fake entry
  at this address and places `processPolledControllerData` at `0x800027C0`.
  It supplies no semantic function name for the two-instruction fragment.
- `syms/rogue_squadron.syms.toml` independently classifies
  `0x800027B8..0x800027C0` as `data_gap_800027B8`, size `0x8`.

The exact span and non-callable generated body select H2. No semantic rename
is justified. The existing regeneration mapping to `data_gap_800027B8` is
consistent with this result; no generated or mapping change is made.

## Next candidate

Continue the same exact-span test with the next remaining live placeholder.
