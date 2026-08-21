# NEXT work unit (s2138) — known-MORT sample decode and PCM contract

HYPOTHESIS-ID: m5-mort-sample-contract

## Work unit

Run one bounded host-only/reference comparison for four retail `speech` MORT
descriptors: indices `0`, `1`, `419`, and `545`, covering both observed sample
rates and multiple descriptor types. Use the retail ROM at
`build/rogue_squadron.z64`, the companion descriptor layout in
`/Users/williambuckley/Documents/Tools/rogue_squadron64/docs/subtitles/subtitles.md`,
and an independent MORT decoder/reference implementation. This is a decode
contract census, not permission to change the port audio arm or to add a new
RSP segment.

## Competing hypotheses and discriminator

- `H-MORTReferenceMatches`: the `speech` asset's 24-bit descriptor offsets,
  `MORT` headers, type byte, rate, and word-count span decode through the
  independent reference into the expected signed-PCM byte count and waveform
  statistics for all four selected descriptors.
- `H-MORTLayoutOrEndianMismatch`: the descriptor table or header interpretation
  is wrong; one or more selected offsets, rates, word counts, or compressed
  spans fail the companion layout checks before decoding.
- `H-MORTCodecVariantMismatch`: headers and spans are valid, but the reference
  decoder's output count or waveform hash/min-max differs for a type/rate
  class, indicating a codec variant or block-state mismatch.
- `H-MORTReferenceUnavailable`: no independent decoder can be built or the
  output cannot be tied to a descriptor with a positive control, so the result
  is unresolved rather than a null decode.

The single discriminating table is one row per selected descriptor with ROM
offset, type, rate, word count, compressed bytes, decoded samples/bytes,
nonzero count, FNV, min/max, and first/last sample. The positive controls are
`546` descriptors, all `MORT` headers, the companion type distribution
`419/59/36/17/9/6`, and both `8000`/`16000` rates. Select
`H-MORTReferenceMatches` only if every selected row has a valid header/span
and the independent decoder produces a stable PCM row; otherwise select the
specific layout/variant hypothesis or `H-MORTReferenceUnavailable`. Do not
interpret a parser-only success as decoded audio evidence.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    mkdir -p scratch/agent/s2138_mort
    git clone --depth 1 https://github.com/jombo23/N64-Tools.git scratch/agent/s2138_mort/N64-Tools
    rg --files scratch/agent/s2138_mort/N64-Tools | rg 'MORTDecoder\.cpp$'

Before adding the table harness, verify the independent source and the
companion layout. If the clone is unavailable, use the exact source already
referenced by the companion notes only after recording that limitation; do not
substitute the recompiled game for the reference. Add the bounded harness as
`tools/mort_probe.py` with `apply_patch`, then run:

    python3 tools/mort_probe.py --rom build/rogue_squadron.z64 --speech-offset 0x583D90 --speech-size 0x31D3E4 --indices 0,1,419,545 --reference scratch/agent/s2138_mort/N64-Tools/N64SoundListToolUpdated/N64SoundLibrary/MORTDecoder.cpp > scratch/agent/s2138_mort/result.log
    sed -n '1,120p' scratch/agent/s2138_mort/result.log

The harness must fail closed if it cannot decode a row or if the independent
reference does not expose a callable decoder. No game build or runtime change
is in scope. If the four-row table is not fully discriminating, stop and write
the unresolved table into `NEXT.md` rather than adding another field or
running a second decode recipe.
