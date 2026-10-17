# Generated-symbol audit — `strchr`

## Candidate

- Symbol: `strchr`
- Address: `0x80034744`
- Companion range: `0x80034744` through `0x80034790`
- Hypothesis: `generated-symbol-renaming-sweep`

## Discriminator

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. Independent generated-tree inspection found a real
`strchr_recomp` body beginning at `0x80034744`, ending at `0x80034790`, and an
overlay record with `rom_size = 0x4C`, exactly matching that span. Six
generated call sites target `strchr_recomp` in addition to its definition.

## Result

This is the H-generated-name-correct outcome. Preserve the existing semantic
ABI name `strchr`; no generated-symbol rename or build/soak was warranted.
The result rules out a placeholder, host-wrapper-only entry, and span
mismatch for this candidate, but says nothing about libc wrapper runtime
behavior.
