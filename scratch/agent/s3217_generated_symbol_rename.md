# Session 3217 — excluded overlapping live-tail symbol

The bounded audit of `func_80092F10` selects `H-DataOrGap`, not a rename.

| Evidence key | Result | Discriminator |
|---|---|---|
| TOML range | `func_80092F10` is listed at `0x80092F10`, size `0x84`, ending at `0x80092F94` | The next generated function starts exactly at the claimed end, so the entry has no generated callable body of its own |
| Generated body | `resampleVoiceLutSamplesPacked` is emitted at `0x80092E48`; `packFourLutResampledSamples` is emitted at `0x80092F94` | The apparent `0x80092F10` label is inside the preceding function's epilogue/inline control flow and is not a `RECOMP_FUNC` boundary |
| Calls | The only calls in this region target `0x80092F94`, emitted as `packFourLutResampledSamples`; no call targets `0x80092F10` | No callable fan-in exists for the candidate |
| Companion symbols | `main_overlay.txt` names `0x80092F94` `packFourLutResampledSamples`; its audio family names the surrounding functions but has no semantic name at `0x80092F10` | Independent metadata agrees with the generated boundary and supplies no candidate name |
| Registration | `funcs.h` declares `packFourLutResampledSamples`, but no declaration or registration exists for `func_80092F10` | The candidate is not an independently dispatchable function |

The competing `H-RealFunction` hypothesis is ruled out at the available source
boundary: there is no callable body, fan-in, or registration to name. The
`H-Unresolved` hypothesis is also not the best classification because the
overlap and exact next-function boundary explain the TOML entry. No generated
file was edited and no runtime run was warranted.

Independent lines of evidence are the generated function/call boundaries and
the companion symbol/declaration metadata. This is a data-gap exclusion, not a
claim about the audio algorithm itself.
