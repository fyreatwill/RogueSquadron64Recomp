# NEXT work unit (s1133)

HYPOTHESIS-ID: animation-framestart-regeneration-omission

Perform one bounded static census of the isolated animation/frameStart SIGBUS
and its possible regeneration omission. Do not build or run. First enumerate
all generated references and fixup-script references for the implicated
function/site, then classify each as regenerated, fixup-restored, or absent.

Competing hypotheses and discriminator:

- H-regenerated: the expected animation/frameStart function and call/data
  references are present in generated output; the SIGBUS is runtime state.
- H-fixup-restored: generated output omits the site, but a fixup script restores
  it deterministically during regeneration.
- H-omitted: both generated output and fixup scripts omit the expected site,
  making regeneration loss the actionable defect.

Discriminator: a complete reference/fixup census with every expected address
classified. Presence in generated code selects H-regenerated; absence there
but an explicit fixup match selects H-fixup-restored; absence in both selects
H-omitted. Any unclassified reference means the audit is inconclusive.

Do not build or run. Use bounded windows only:

```sh
rg -n 'frameStart|animation|0x800[0-9A-Fa-f]{4}' ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n 'frameStart|animation|0x800[0-9A-Fa-f]{4}' tools patches docs
```
