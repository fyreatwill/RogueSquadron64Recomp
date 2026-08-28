# NEXT work unit (s2884) — generated-symbol renaming sweep continuation

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run one bounded, source-backed generated-symbol sweep immediately after
`0x800BAA00`, continuing the existing synchronized companion-map campaign.
Before selecting the interval, run the required `PORTING-STATE.md` title check
to detect a sweep-only revisit. Rename only records with a defensible
companion/m2c semantic name or mechanically proven short data-gap body; leave
callable-ambiguous and data-ambiguous records unchanged.

## Competing hypotheses and discriminator

- H-RealName: companion source and local semantics prove a human symbol name.
- H-DataGap: the record is a non-callable short data/trap gap with a stable
  `data_gap_*` name.
- H-Ambiguous: evidence is insufficient; the placeholder must remain.

The single discriminating measurement is one interval census joining every
placeholder to its companion symbol, body size/kind, callers, and local
semantic evidence. Each record must land in exactly one of the three classes;
only the first two classes authorize a rename.

## Exact next commands

1. Run `grep -n '^## Session ' PORTING-STATE.md | tail -15` and apply the
   sweep-only revisit rule from the autonomous-iteration instructions.
2. Inspect the next bounded generated interval after `0x800BAA00` using the
   existing companion maps, fixup script, and generated snapshot. Do not
   regenerate the main tree.
3. Apply only source-backed renames through
   `tools/rename_generated_symbols.py`; record every examined address and
   classification in `scratch/agent/s2884_generated_symbol_rename/`.
4. Verify the changed references and run the focused symbol/fixup checks.

## Expected outcomes

- A proven companion semantic name authorizes a human rename.
- A proven short non-callable gap authorizes `data_gap_*`.
- Any ambiguity leaves the placeholder unchanged and advances the interval
  census without inventing a name.
