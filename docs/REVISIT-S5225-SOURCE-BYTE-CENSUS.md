# Session 5225 — mission-entry s0 census

Question: is the modal mission-entry `s0+0x22` inside one of the two words
guessed from session 5223's first three samples (`0x191070:0x191074` and
`0x1951B0:0x1951B4`), and if so which retail PC writes it?

## Controls

Port run `scratch/agent/s5225_port_s0/run.log`, SIGKILL at stop_t=404.
`[s5223-armed]` fired once. Title, hangar, and `origin=0x00620400` were
present. No crash marker. The driver summary says the census is absent;
that file keys the origin on six hex digits and misses `00690400`. The log
itself has 1729 `[s5225-s0]` leave lines, and the last leave per origin
reparsed with slot counts plus overflow equal to the entry count:
`0x00690400` entry=80256 slots=64 overflow=14 sum=80256;
`0x00620400` entry=79505 slots=64 overflow=34 sum=79505.

Retail run `scratch/agent/s5225_retail_writer/oracle.log` stopped itself
(`killed_overrun=0`). Whole-RDRAM watch index 0 reached 10000 writes at
vi=1 and was removed. VI trace reached both mission origins. Phase rows:
`0x00690400` width 512, 4314 frames; `0x00620400` width 512, 4179 frames.
Census sums equal the hit counts: 125333 and 125480, 41 slots, overflow 0
on both. The entry watch at `0x8008FAAC` counted 557582 hits.

## Census

Retail `s0` on both origins is the 41-address run
`0x80190E50 + i*0x88` (`i=0..40`). Counts are flat (about 3% each). The
highest is `0x80190E50` at 4220/125333 and 4186/125480. Its source byte is
physical `0x190E72`. No retail `s0+0x22` falls in either watched word.
Retail never uses `s0=0x80195190`.

The port uses that same stride and a second stride-`0x88` run whose base
is `0x80195190`. That second base is the only census address whose
`s0+0x22` (`0x1951B2`) sits in a watched word, and only on the port
(2687/80256 and 2669/79505).

## Writers of the guessed words

`writer-pc-phase` printed the four headers and no `pc=` rows. During both
mission origins, nothing wrote either watched word.

Lifetime, outside those phases: watch 1 (`0x191070`) had 8 writes,
`0x80018F5C` (`sd $t1, 0($t5)`) and `0x800078EC` (`sb $a1, 0($v0)`), 4
each. Watch 2 (`0x1951B0`) had 26681 writes. The stores that touch offset
`0x22` are `0x80090F3C` (`sb $zero, 0x22($v0)`, 8789) and `0x80090F8C`
(`sb` of the constant 1, 306). `0x80090720` and `0x80090780` write offsets
`0x20` and `0x21` of the same word. `$v0` at the `0x22` stores is
`base + index*0x88`. Neither store can write `0x03`. They are not
mission-phase writers of the retail bytes, because those bytes were not
in the watched words.

## Selection

This selects H-wrong-candidate. It refutes H-same-writer-different-value
and H-different-writer for these two words: the words do not contain the
bytes the census reads. No guard. The next watch list is the retail bytes
`0x190E72 + i*0x88`, as the aligned words `0x190E70 + i*0x88`.
