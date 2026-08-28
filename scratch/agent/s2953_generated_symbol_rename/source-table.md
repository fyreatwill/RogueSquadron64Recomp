# Generated-symbol sweep: `0x8009D978`

Candidate: `0x8009D978`, project symbol `func_8009D978`, size `0x8`.

## Competing hypotheses and discriminator

| Hypothesis | Predicted evidence | Decision rule |
|---|---|---|
| H-Callable | Standalone prologue/return plus an independent caller or exact companion semantic name | Rename to that semantic name |
| H-Fragment | Valid instructions form a split executable fragment, but no independent entry/caller/name exists | Preserve address identity unless a stronger classification is available |
| H-DataGap | Bytes are mechanically non-callable data or a recompiler false split between complete functions | Rename mechanically to `data_gap_8009D978` |

The discriminator is the complete generated span and its exact neighboring
bodies, combined with caller/lookup and companion-map searches.

## Evidence

| Evidence | Result | Implication |
|---|---|---|
| Exact span and boundaries | `applyVoiceDelayFilter` occupies `0x8009D8C4..0x8009D977` and returns at `0x8009D970/0x8009D974`; `runVoiceLatticeFilter` begins at `0x8009D980` with a normal `lh` prologue instruction. The candidate is exactly the intervening 8 bytes. | No standalone prologue or return exists in the candidate. |
| Generated decode | `funcs_27.c` reaches `L_8009D978` only through the never-taken `bltzal $zero` PC-capture idiom in `applyVoiceDelayFilter`. The generated record is emitted as `jal 0x8334B334` plus a cross-function branch trap in `funcs_49.c`. | The callable-looking generated body is a false split, not an independently callable routine. |
| Retail bytes / semantic control | The independent retail source inventory records file words `0x0CCD2CCD` and `0x53337FFF` at `0x8009D978`, the Q15 coefficient values used by the following voice filter; the next word at `0x8009D980` is `0x852A0000` (`lh $t2, 0($t1)`). | The candidate is a coefficient table immediately before live code, not executable code. |
| Callers and lookups | The bounded repository search found no `jal`, `j`, absolute pointer, or independent generated caller targeting `0x8009D978`; the only generated reference is the internal false branch target. | No independent callability. |
| Companion map | `main_overlay.txt` names `applyVoiceDelayFilter` at `0x8009D8C4` and `runVoiceLatticeFilter` at `0x8009D980`, with no symbol at `0x8009D978`. The companion audio notes identify the 8 bytes as a coefficient table. | Adjacent semantic boundaries agree; no callable name exists. |

## Classification

The evidence selects **H-DataGap**. The candidate is a mechanically
non-callable eight-byte coefficient table misdecoded as a false branch-target
function. It is renamed `data_gap_8009D978` in the project symbol map, the
regeneration-safe rename table, and the generated declaration/definition and
internal reference. No gameplay or runtime behavior was changed.
