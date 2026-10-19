# M3 audit: late `$ra` writes before `jr $ra`

Class: generated return blocks where `$ra` is written after the last call or
immediately before a `jr $ra`.

## Census

`python3 tools/audit_ra_return_idiom.py` scanned all 51 generated files and
2,502 `RECOMP_FUNC` bodies in the companion `../N64Recomp/RecompiledFuncs`
tree. It found 1,884 `ctx->r31` assignments, 42,504 `jal`/`jalr` comment
sites, and 2,543 `jr $ra` comments. Of the return blocks, 1,686 had a prior
`r31` assignment; 1,653 ended with a normal `MEM_W(ctx->r29, ...)` restore.
The positive controls were present: `loadOverlay` is an ordinary saved-`ra`
epilogue and `audioMixStereoBlock8` is a computed/tail-return shape.

The raw late-write list had 25 rows, but it collapses to four source classes:

| Sites | Class | Disposition |
|---:|---|---|
| 10 | `data_gap_80099FDC` in `funcs_26.c` | Invalid/data-gap material, not a callable body |
| 6 | `data_gap_80024A0C` in `funcs_7.c` | Invalid/data-gap material, not a callable body |
| 8 | `filterVoiceSampleBlock`, `applyVoiceDelayFilter`, `renderVoiceAudioBlock` in `funcs_27.c` | Factor 5 voice fragments use `bltzal`/computed return-address transfer; generated duplicated delay/control-flow blocks, not a late ordinary return clobber |
| 1 | `audioMixStereoBlock8` in `funcs_27.c` | Intentional computed/tail return (`addu $ra, $t5, $zero`) after indirect calls |

The eight voice-fragment rows include the explicit generated link writes for
the `bltzal` fragments and the subsequent `$ra` restoration/transfer. The
five data-gap rows in each gap are embedded invalid/data material rather than
reachable prologue-to-epilogue functions. No candidate is a reachable ordinary
function that clobbers a saved return address after its last call.

## Verdict

H3 selected: the apparent late writes are delay-slot/control-flow artifacts,
computed/tail returns, or invalid/data-gap material. No guard or runtime change
is authorized. Re-open only if a backtrace identifies one of these fragments on
an ordinary return path or regeneration changes the census.
