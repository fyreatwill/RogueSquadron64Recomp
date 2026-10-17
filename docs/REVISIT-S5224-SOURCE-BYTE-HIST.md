# Session 5224 source-byte frequency histograms

Question: on the mission origins, is the port's modal `source_byte` at
`s0+0x22` outside the byte set retail actually emits, or did session 5203's
32768-row cap hide the common retail byte?

## Controls

Port run `scratch/agent/s5224_source_byte_hist/run.log`, SIGKILL at
stop_t=404. `[s5223-armed]` fired once. Title `origin=0x00790400` was
present. No crash marker. The last `[s5224-hist]` leave line for each
mission origin has 256 bins whose sum equals that line's entry count
(79362 and 79498). 195 earlier lines were torn by concurrent stderr and
were not used.

Retail run `scratch/agent/s5224_retail_hist/oracle.log` stopped itself at
420.3s wall, 25177 VI (~419.6s emulated), `killed_overrun=0`. The
whole-RDRAM write watch reached 10000 callbacks at vi=1 and was removed
(rc=0). That is 10000 writes in one frame, about 4.8M writes in 8 emulated
seconds, above the ~1.6M bar. The exec watch armed at
`[phase-arm] width=512 origin=0x00690400`. VI trace reached title, hangar
`0x006AB400`, and both mission origins. Phase frame counts were 4158 and
4258. Both histogram bin sums equal their hit counts.

## Frequency

Retail `0x00690400`, 121195 hits: `0x00` 119949 (98.972%), `0x01` 1244
(1.026%), `0xF0` 2, `0x03` 0, `0xFF` 0.

Retail `0x00620400`, 127740 hits: `0x00` 126435 (98.978%), `0x01` 1304
(1.021%), `0x0C` 1, `0x03` 0, `0xFF` 0.

Port `0x00690400`, 79362 entries: `0x03` 79212 (99.811%), `0x00` 110,
`0x01` 2, `0xFF` 2, `0xBB` 1.

Port `0x00620400`, 79498 entries: `0x03` 79385 (99.858%), `0x00` 95,
`0x01` 1, `0xFF` 0, `0xBB` 0.

## Selection

This selects H-port-byte-diverges. It refutes H-retail-cap-blind: counting
hits the unique-row cap would have dropped, retail's modal byte is `0x00`
and its `0x03` bin is empty, while the port's modal byte is `0x03`. The
field difference is real. No guard. The writer of the byte is the open
question, not another entry field.
