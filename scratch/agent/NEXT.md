# BEGIN generated-symbol-renaming sweep after M3 dispatch audit

HYPOTHESIS-ID: generated-symbol-renaming-sweep

The s4998 M3 indirect-call audit closed that class. M5 is fully closed through
the long mission hold. The last-15-session preflight is not sweep-only, so the
symbol sweep is eligible. Do not revisit the stale voice-count sample.

Competing hypotheses:

1. H-companion-match: one placeholder has an exact companion/decomp mapping
   and can be renamed without changing generated behavior.
2. H-no-safe-map: the next ranked placeholder lacks a companion, live-caller,
   or exact-span match and must remain `func_*`.
3. H-stale-generated-name: the candidate is already human-named in the
   companion but not synchronized in the generated/fixup symbol map.

Discriminating outcomes:

- An exact mapping with matching address, body span, and a live caller selects
  H-companion-match and lands one regeneration-safe symbol-map rename.
- Any failed gate selects H-no-safe-map; leave the placeholder unchanged and
  record why.
- A generated/fixup mismatch selects H-stale-generated-name and synchronizes
  only the mapping source, with no hand edit to generated C.

Exact next commands:

    grep -n '^## Session ' PORTING-STATE.md | tail -15
    rg -n 'func_8000040C|func_800E9AE0' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs tools docs
    sed -n '1,220p' tools/rename_functions.py 2>/dev/null || true

Before any build, write the candidate table and exact mapping discriminator
here. If an exact mapping exists, apply it through the existing rename/fixup
source, run its checker, and commit the mapping plus a concise audit note.
