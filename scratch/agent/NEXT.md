# NEXT work unit — bounded M3 audit of `musyxInitVoiceFromSample` descriptor producers

HYPOTHESIS-ID: m3-idiom-audit

## Single work unit

Audit the unresolved descriptor-pointer edge at `musyxInitVoiceFromSample`
(`0x80092128`). Enumerate both generated callers, the complete construction
and writer inventory for their `$a1` sample descriptor, all pointer/range
checks and dispatch edges, and companion symbol/ELF metadata. Static audit
only: no build, run, guard, or audio change.

Competing hypotheses and discriminating measurement:

- `H-M3-Proven`: both reachable callers pass a live, bounded descriptor
  pointer whose fields are valid for the callee's reads.
- `H-M3-Unclassified`: a reachable caller lacks that proof, or descriptor
  population is through an unrecovered data/DMA/indirect producer; this is not
  proof of a retail-invalid pointer.
- `H-M3-Dead`: the apparent call/access is unreachable or lowering-only.

The discriminator is one complete caller/producer table with guest PCs,
argument construction, descriptor writers, range checks, dispatch edges, and
independent companion symbol/ELF confirmation. A fully bounded table selects
Proven; an unbounded or unrecovered reachable producer selects Unclassified;
no reachable call selects Dead.

Exact starting commands:

```sh
rg -n 'musyxInitVoiceFromSample|0x80092128|0x8009212C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n 'musyxInitVoiceFromSample|0x80092128|sampleDesc|sample' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files /Users/williambuckley/Documents/Tools/rogue_squadron64/build
```

Expected outcome: a complete static table selects exactly one of
`H-M3-Proven`, `H-M3-Unclassified`, or `H-M3-Dead`; no runtime probe or build
is authorized.
