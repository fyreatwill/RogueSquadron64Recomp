# NEXT work unit — trace the upstream argument supplying 0x8009123C

HYPOTHESIS-ID: m5-callback-table-writer

Session 3361 paired the port callback-table store: `0x80007928` wrote
`0x8009123C`, `0x80007968` cleared, and `0x80017D08` wrote only `0x400/0x800`
halfwords. The remaining boundary is upstream of the known table store: what
caller/path supplies `0x8009123C` as the argument to the indirect callback
registration chain.

Competing hypotheses:

- `H-ArgFrom919ECCaller`: the caller of the `0x800919D4/0x800919EC` chain
  supplies `0x8009123C` directly in its argument register.
- `H-ArgFromEarlyInit`: an earlier initialization path leaves the argument
  in a shared state/register before the indirect chain runs.
- `H-ArgFromUnresolvedJalr`: another register-loaded indirect caller reaches
  the same registration target with the value.
- `H-ArgHostDispatch`: host/runtime dispatch changes the argument before the
  guest registration store.

Discriminating measurement: perform one bounded static census of every
generated call/edge into `0x800919D4` and `0x800919EC`, including the
immediately preceding assignments to the argument register, and compare it
with the existing runtime row `0x800919EC -> 0x80007910, a0=0x8009123C`.
Every possible result must classify the source as a concrete guest caller,
an earlier state load, an unresolved jalr, or no guest source (host path).

Before building, use only bounded searches around the two symbols and read
`docs/F5-UCODE-REFERENCE.md` only if the edge is confused with a rendering
path. Do not add a runtime counter or change behavior unless the static
census finds a specific missing edge that can be instrumented as one table.
If instrumentation is required, update its fixup source before regeneration.
The existing validated run recipe remains:

```sh
rg -n -C 8 '800919D4|800919EC|LOOKUP_FUNC' ../N64Recomp/RecompiledFuncs/funcs_*.c
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Retain the retail whole-RDRAM/callback-slot positive controls and port
host/task/PCM/title/hangar controls for any runtime follow-up.
