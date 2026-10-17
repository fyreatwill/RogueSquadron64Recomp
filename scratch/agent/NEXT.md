# Next: classify `__osViNext = 0x80039214`

The previous unit classified `__osViCurr = 0x80039210` as typed data. Run the
same bounded generated-symbol discriminator for the next companion record.

Competing hypotheses and discriminator:

- H1: `__osViNext` is typed data and already has no callable generated body.
- H2: it is an unmaterialized callable placeholder that the helper missed.
- H3: it is a generated callable/data fragment whose name needs a semantic
  correction.

Discriminating measurement: run the bounded helper over
`0x80039214..0x80039220`, then independently inspect the companion type and
generated tree for a body, placeholder, declaration, overlay record, and
direct reference. H1 is selected by typed data plus no generated callable;
H2 by a callable placeholder/body; H3 by a callable fragment or conflicting
semantic record. Do not build or soak this naming-only unit.

Exact command:

`python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x80039214 --end-address 0x80039220 --limit 1`

HYPOTHESIS-ID: generated-symbol-renaming-sweep
