# Session 3175 generated-symbol sweep

The bounded regeneration-safe sweep covered `0x80120000..0x80130000` with
`--limit 16 --require-rename`.

The positive-control classifier fired: it listed companion records as
`already-synchronized` and `ambiguous-or-fake`, including the in-band data
records at `0x80128C80` and `0x80128CE0`. The helper then returned its expected
no-rename error, changing `0` references in `0` files. This confirms the census
was active rather than silently finding no candidates.

An independent generated-definition search for `RECOMP_FUNC` bodies named
`func_*`, `fake_func_*`, or `static_*` in the interval returned `0` matches.
The same placeholder-definition search positively matched known out-of-band
records (`fake_func_800027B8`, `fake_func_800AE3E4`), confirming the search
pattern was live.

Conclusion: this interval contains no stale generated semantic placeholder
definition or exact companion rename. Synchronized records are closed; the
ambiguous/fake records remain untouched. No build or game run was needed.
