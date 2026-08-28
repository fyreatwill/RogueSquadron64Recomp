# Session 2908 generated-symbol interval table

Interval: `0x8004661C..0x80046620` (end exclusive)

| Record | Generated body and boundaries | Companion/source evidence | Callers/lookups | Action |
|---|---|---|---|---|
| `0x8004661C` (`fake_func_8004661C`) | 4 bytes; one `addiu $sp,$sp,0x30`, with no return, body, or epilogue. It immediately precedes the complete `parseDatItemCommon` entry at `0x80046620`, whose body returns at `0x8004677C`. | Companion map had only the placeholder and no semantic name; the decomp source names the following callable `parseDatItemCommon` at `0x80046620`. | No generated callers or address lookups for `0x8004661C` beyond overlay metadata. | H-DataGap -> `data_gap_8004661C` |

The record is mechanically non-callable as emitted: its only instruction is a
stack adjustment and it has no return or independent body. The adjacent
callable is already named and starts at the next address.
