# Session 2902 generated-symbol interval table

Source snapshot: `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs.s2471-gate3-before`.
Companion sources: `rogue_squadron64/symbol_files/zlib.txt` and
`rogue_squadron64/symbol_files/libultra.txt`.

## Interval inspected

`0x80029D20 <= address < 0x8002A080`, from the established
`osAiSetFrequency` boundary through the established `bzero` boundary.

| Range | Generated entry | Companion entry | Evidence | Decision |
|---|---|---|---|---|
| `0x80029D20..0x80029E7F` | `osAiSetFrequency` | `osAiSetFrequency` | Established callable symbol; no placeholder | Keep |
| `0x80029E80..0x80029F2F` | `osAiSetNextBuffer` | `osAiSetNextBuffer` | Established callable symbol; no placeholder | Keep |
| `0x80029F30..0x80029F5F` | `__osAiDeviceBusy` | `__osAiDeviceBusy` | Established callable symbol; no placeholder | Keep |
| `0x80029F60..0x8002A07F` | `bcmp` | `bcmp` | Established callable symbol; no placeholder | Keep |

Independent generated-definition scan found zero `func_*` or `fake_func_*`
definitions in this interval. Therefore no callable rename, data-gap rename,
or ambiguous placeholder was selected, and no regeneration mapping changed.

The next unresolved generated placeholder in ascending address order is
`fake_func_8003DF98`, outside this interval; its companion map already labels
that record `data_gap_8003DF98` and it is deferred to the next work unit.
