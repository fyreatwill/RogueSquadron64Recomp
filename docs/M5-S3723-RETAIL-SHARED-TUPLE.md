# M5 s3723 — retail shared guest-field tuple

## Work unit

Ran one independent retail-oracle capture with a whole-RDRAM positive control,
both 512-wide origins (`0x006AB400` and `0x006AB800`), and execution/field
watches for `0x80033FCC`, `0x80029E80`, `0x80029F30`, and `0x80094648`.

## Result

The oracle exited `rc=0`. The positive-control threshold reached 10,000
writes. Both target origins were reached. The two shared-tuple PCs each
produced field rows at both target origins:

| PC | `s0` | `s1` | `source_byte` | `branch_state` | field rows |
|---|---|---|---|---|---:|
| `0x80029E80` | `0x801496B0` | `0` | `0x7C` | `0x0010` | 335 + 286 |
| `0x80029F30` | `0x801496B0` | `0` | `0x7C` | `0x0010` | 335 + 286 |

The first count is origin `0x006AB400`; the second is `0x006AB800`.
Independent execution-watch rows also paired the two PCs at both origins,
with matching `s0`, `s1`, source byte, and branch state. The `0x80094648`
rows remained a distinct path: 64 field rows at each origin, with changing
`s0`/`s1` context. `0x80033FCC` likewise remained distinct.

## Interpretation

This selects `H-SharedTupleIntentional` for `0x80029E80` and `0x80029F30`.
It refutes `H-SharedTuplePhaseAlias` for the measured origin/phase buckets
and provides no support for `H-SharedTupleFieldArtifact`: both the field dump
and the independent execution-watch register rows agree. The result does
not establish host callback or SDL queue parity; those remain downstream
open questions.

Evidence: `scratch/agent/oracle_s3723_retail_shared_tuple/oracle.log`.
