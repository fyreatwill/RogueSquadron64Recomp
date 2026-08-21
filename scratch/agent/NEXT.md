# NEXT work unit (s2139) — cover MORT rate/type classes

HYPOTHESIS-ID: m5-mort-sample-contract

## Work unit

Run one bounded host-only/reference comparison with the existing
`tools/mort_probe.py` harness for indices `4,58,90,104`. These rows cover
descriptor types 1 and 2 at 8000 Hz plus types 3 and 5 at 16000 Hz. The
s2138 mandated table decoded indices `0,1,419,545`, but all four were
descriptor type 0 at 8000 Hz, so it did not discriminate the uncovered rate
or descriptor-type classes.

The unresolved s2138 table was:

| index | descriptor type | rate | word count | decoded samples | nonzero | FNV |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 8000 | 4 | 2240 | 157 | `0xA667793D` |
| 1 | 0 | 8000 | 678 | 13440 | 13210 | `0xA28B37D0` |
| 419 | 0 | 8000 | 249 | 6080 | 4783 | `0xF166120B` |
| 545 | 0 | 8000 | 843 | 18880 | 16344 | `0xFB04E2D2` |

No game build, runtime change, task-field change, output-route change, or
default-arm change is in scope.

## Competing hypotheses and discriminator

- `H-MORTReferenceMatchesExtended`: all four uncovered-class rows pass the
  independent decoder and produce stable nonempty PCM statistics, extending
  the reference contract across both observed rates and multiple descriptor
  types.
- `H-MORTLayoutOrEndianMismatch`: a selected descriptor fails the MORT header,
  bounds, rate, word-count, or descriptor-type checks despite the global
  positive controls.
- `H-MORTCodecVariantMismatch`: headers and spans are valid, but a rate/type
  class fails to decode or has an unstable/empty output row, indicating a
  codec block-state or variant boundary.
- `H-MORTReferenceUnavailable`: the independent source cannot be compiled or
  called, or the returned table is incomplete; this is unresolved rather
  than a codec null.

The one discriminating measurement is one row per selected descriptor with
descriptor identity, type, rate, word count, compressed bytes, decoded
samples/bytes, nonzero count, FNV, min/max, and first/last sample. The same
run must print the positive controls: 546 descriptors, all MORT headers,
type counts `419/59/36/17/9/6`, and rates `8000:440`/`16000:106`. Do not add
another field or run a second decode recipe if this table remains
non-discriminating.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    mkdir -p scratch/agent/s2139_mort
    python3 tools/mort_probe.py --rom build/rogue_squadron.z64 --speech-offset 0x583D90 --speech-size 0x31D3E4 --indices 4,58,90,104 --reference scratch/agent/s2138_mort/N64-Tools/N64SoundListToolUpdated/N64SoundLibrary/MORTDecoder.cpp > scratch/agent/s2139_mort/result.log
    sed -n '1,120p' scratch/agent/s2139_mort/result.log

Expected outcomes: four complete rows with both rates and multiple types
select `H-MORTReferenceMatchesExtended`; a layout failure selects
`H-MORTLayoutOrEndianMismatch`; a valid-header decode failure selects
`H-MORTCodecVariantMismatch`; and a compile/call/incomplete-table failure
selects `H-MORTReferenceUnavailable`. Keep the reference source external and
fail closed on any missing row.
