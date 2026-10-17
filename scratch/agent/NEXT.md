# Next: continue the generated-symbol sweep

Classify the next companion record after `__osViNext = 0x80039214` with the
same bounded generated-symbol helper and independent companion/generated-tree
inspection. Determine the exact next address/name from the companion map
before running the helper. Do not build or soak unless the discriminator finds
a callable placeholder or a needed rename.

Competing hypotheses and discriminator:

- H1: the next record is typed data or an already-synchronized ABI symbol.
- H2: it is an unmaterialized callable placeholder that the helper missed.
- H3: it is a generated callable/data fragment whose name needs correction.

Discriminating measurement: helper result plus independent checks for a
companion type, generated body, placeholder, declaration, overlay record, and
direct generated reference. H1 is selected by typed data/no callable; H2 by a
callable placeholder/body; H3 by a callable fragment or conflicting semantic
record.

HYPOTHESIS-ID: generated-symbol-renaming-sweep
