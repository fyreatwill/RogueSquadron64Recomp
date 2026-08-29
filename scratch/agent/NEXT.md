# NEXT work unit — bounded M3 audit of the `musyxStoreVoiceAdsrParams` index producer

HYPOTHESIS-ID: m3-idiom-audit

## Single work unit

Audit the unresolved byte-loaded voice-index edge at `0x8008A9D8`:
`musyxSetVoiceAdsrFromTable` loads its caller-owned record byte at `+0x67`
and passes it to `musyxStoreVoiceAdsrParams` (`0x800922C4`), which computes a
`0x88`-stride voice record and has only a base-pointer guard. Enumerate every
reachable caller, every writer or construction path for the owning `+0x67`
field, all range checks and dispatch edges, and independent companion
symbol/ELF metadata. Static audit only: no build, run, guard, or audio change.

Competing hypotheses and discriminating measurement:

- `H-M3-Proven`: every reachable producer of the `+0x67` byte proves a valid
  mixer voice index for the callee's `0x88`-stride access.
- `H-M3-Unclassified`: at least one reachable producer lacks that proof, or
  the field is populated through an unrecovered data/DMA/indirect edge. This
  is a contract classification, not proof of a retail-invalid value.
- `H-M3-Dead`: the apparent caller/site is unreachable or only a generated
  lowering artifact.

The discriminator is one complete table with guest PC, caller, owner-record
construction, all `+0x67` writers/readers, range checks, dispatch edges, and
companion symbol/ELF confirmation. A fully bounded table selects Proven; a
reachable unbounded or unrecovered producer selects Unclassified; no
reachable site selects Dead.

Exact starting commands:

```sh
rg -n 'musyxStoreVoiceAdsrParams|musyxSetVoiceAdsrFromTable|0x67|0X67' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n 'musyxStoreVoiceAdsrParams|musyxSetVoiceAdsrFromTable|0x800922C4|0x8008A9D8' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files /Users/williambuckley/Documents/Tools/rogue_squadron64/build
```

Expected outcome: a complete static table selects exactly one of
`H-M3-Proven`, `H-M3-Unclassified`, or `H-M3-Dead`; no runtime probe or build
is authorized.
