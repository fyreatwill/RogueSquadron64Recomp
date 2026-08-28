# Session 2974 generated-symbol rename table

The bounded batch was selected from the generated placeholder list and checked
against the adjacent generated routine and companion symbol map before editing.

| Address | Generated body | Boundary evidence | Companion successor | Decision |
|---|---|---|---|---|
| `0x80055A2C` | one `subu` instruction | ends immediately before independent prologue at `0x80055A30` | `initVoiceSubtitleSystem` | `initVoiceSubtitleSystemPreamble` |
| `0x80072CE8` | `addiu` plus `addu` | ends immediately before independent prologue at `0x80072CF0` | `initWaterSprayParticles` | `initWaterSprayParticlesPreamble` |
| `0x8009D7CC` | one `mtc1` instruction | ends immediately before independent entry at `0x8009D7D0` | `filterVoiceSampleBlock` | `filterVoiceSampleBlockPreamble` |

Each record is a short entry fragment, not a standalone routine: there is no
independent return or callable body boundary, and the next routine has the
semantic companion name. The exact names were added to the regeneration-safe
rename table and companion map, then the rename tool changed three references
in each of the affected generated C/header/overlay files. The generated
functions target built successfully.

The competing outcomes were: semantic successor evidence (selected), an
ambiguous/data-gap boundary (would remain unchanged), or source disagreement
(would stop the batch). No game behavior or runtime mitigation was changed.
