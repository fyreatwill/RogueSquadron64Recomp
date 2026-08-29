# Session 3089 generated-symbol audit — `0x8009C2C8`

## Decision

Selected H-Fragment. The record is named mechanically
`data_gap_8009C2C8`; no callable semantic name is justified.

## Six-surface evidence

| Surface | Observation |
|---|---|
| Companion map | `main_overlay.txt` had only the placeholder at `0x8009C2C8`; the next independent symbol is `computeVoicePanCoefficients` at `0x8009C2D0`. |
| Generated body | The 8-byte body contains only `mul.s $f2,$f2,$f4` and `add.s $f0,$f0,$f2`. |
| Callers | No generated caller references the placeholder; only its declaration and definition existed. |
| Header | `funcs.h` declared the same 8-byte placeholder entry, with no alternate identity. |
| Overlay registration | `recomp_overlays.inl` placed the 8-byte record at ROM offset `0x0009BE88`, immediately after `stopVoice` and before the complete `computeVoicePanCoefficients` entry. |
| Project TOML | `syms/rogue_squadron.syms.toml` specified the exact 8-byte extent at `0x8009C2C8`, bounded by `stopVoice` and `computeVoicePanCoefficients`. |

The companion map and redefs now use `data_gap_8009C2C8`, and the active
generated tree, overlay registration, header, project TOML, and rename map
agree. The generated instructions do not form an independent prologue or
returning body, so this is not an exact callable identity.

No build or runtime run was needed for this static unit.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.
