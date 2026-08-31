# M5 Session 3462 — ordered retail source-writer values

The retail oracle ran for 120 seconds with a whole-RDRAM positive control,
the physical source watch at `0x001E8710:0x001E8714`, title phase logging, and
ordered post-store sampling requested for `0x800644B0` and `0x80064524`.

The whole-RDRAM control reached 12,734 writes and the source watch reached
2,734 writes. The run reached 633 title VI frames. It emitted 1,294 ordered
rows at title origin `0x00790400`: 978 rows from `0x800644B0`, all value
`0x00000000`, and 316 rows from `0x80064524`, with values `0x80194EA0` in 19,
`0x801B4F00` in 165, and `0x801B5E70` in 132 rows.

This is a qualified independent retail table. It selects the ordered-retail
data hypothesis and makes the next discriminator the join against the
existing qualified port title source-writer sequence. It does not by itself
select a port/shared writer explanation.

Evidence: `scratch/agent/s3462_m5_retail_ordered_source/oracle.log`.
