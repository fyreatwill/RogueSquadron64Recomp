# Session 2937 — `0x80092F10` classification

| Field | Evidence | Result |
|---|---|---|
| Address and size | `syms/rogue_squadron.syms.toml` has `func_80092F10`, VRAM `0x80092F10`, size `0x84`; the preceding `resampleVoiceLutSamplesPacked` entry is `0x80092E48`, size `0xC8`, ending at `0x80092F10`. The next independent entry is `packFourLutResampledSamples` at `0x80092F94`, size `0x1B8`. | The TOML record overlaps the live tail of the preceding function and ends at the next independent function boundary. |
| Generated body | `funcs_24.c` defines `resampleVoiceLutSamplesPacked` at `0x80092E48`. Its normal `jr $ra` is at `0x80092F08` with delay slot `0x80092F0C`; the live instructions at `0x80092F10..0x80092F90` pack/zero-fill output and join the wrapper epilogue at `0x80092EE4`. The next generated definition starts at `0x80092F94` as `packFourLutResampledSamples`. | `0x80092F10` is a live internal tail, not a generated function definition. The repeated `L_80092F10` label at the next function is a recompilation label artifact. |
| Predecessor/successor | `resampleVoiceLutSamplesPacked` calls `packFourLutResampledSamples` at `0x80092EBC` and `0x80092EC8`; no generated definition starts at `0x80092F10`. | Ownership is established for the code range, but not by a standalone entry at the candidate address. |
| Companion/m2c evidence | `../rogue_squadron64/symbol_files/main_overlay.txt` names `resampleVoiceLutSamplesPacked = 0x80092E48` and `packFourLutResampledSamples = 0x80092F94`; no `0x80092F10` semantic symbol appears. | No independent semantic name exists. |
| Caller/lookup evidence | Repository search found only the project TOML entry and generated labels/comments; no `jal`, function definition, or independent lookup for `0x80092F10`. | No evidence that the address is callable independently. |
| Callable/data-gap test | The bytes are valid executable instructions and are reached by internal control flow, so they are not an invalid-data filler or dead data gap. They also have no standalone prologue/return. | H-Ambiguous: preserve `func_80092F10` as a TOML-only address-encoded live-tail record; do not rename it or create a `data_gap_*` symbol. |

## Competing hypotheses and discriminator

- H-CallableSemantic: rejected; no independent definition, caller, or companion semantic name.
- H-DataGap: rejected; the range is live packing/zero-fill code owned by `resampleVoiceLutSamplesPacked`, not a data gap.
- H-Ambiguous: selected; the stale TOML entry describes an internal live tail that is non-callable independently but cannot safely be relabelled as data.

No generated source, runtime behavior, or symbol map was changed.
