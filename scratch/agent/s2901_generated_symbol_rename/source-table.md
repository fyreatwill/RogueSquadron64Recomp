# Session 2901 generated-symbol source table

Interval: `0x8002851C..0x80029D20` (the next established boundary after the
last record is `osAiSetFrequency` at `0x80029D20`).

| Address | Size | Companion boundary | Generated body | Calls/lookups | Decision |
|---|---:|---|---|---|---|
| `0x8002851C` | 4 | immediately before `inflate_codes_new` (`0x80028520`) | one isolated `lwc1` | no references outside overlay registration | H-DataGap → `data_gap_8002851C` |
| `0x80028D58` | 8 | immediately before `inflate_fast` (`0x80028D60`) | two isolated `swc1` stores | no references outside overlay registration | H-DataGap → `data_gap_80028D58` |
| `0x800290D8` | 8 | immediately before `huft_build` (`0x800290E0`) | two isolated `lw` loads | no references outside overlay registration | H-DataGap → `data_gap_800290D8` |
| `0x80029B14` | 12 | immediately before `inflate_flush` (`0x80029B20`) | isolated `mul.s`, `sub.s`, `swc1` tail | no references outside overlay registration | H-DataGap → `data_gap_80029B14` |
| `0x80029D14` | 12 | immediately before `osAiSetFrequency` (`0x80029D20`) | isolated `lwc1`, `sub.s`, `swc1` tail | no references outside overlay registration | H-DataGap → `data_gap_80029D14` |

No row had a unique callable companion symbol; no ambiguous row was renamed.
