# Session 3176 — generated-symbol sweep `0x80130000..0x80140000`

The regeneration-safe helper was run with `--require-rename`, selecting the
bounded interval and classifying its companion records. The positive control
fired: the output listed synchronized records including `viEventQueue`,
`gMissionState`, `gPlayers`, `subtitleSlots`, and related data, plus
ambiguous/fake records. It selected no generated references for renaming,
changed zero references in zero files, and returned the expected no-rename
error.

An independent search of generated `RECOMP_FUNC` definitions for
`func_`, `fake_func_`, or `static_` names in the interval produced no rows.
Therefore this band contains no stale callable placeholder body supported by
the companion census. Ambiguous/fake records remain unchanged. No build,
game run, or runtime behavior changed.
