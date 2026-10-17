# Both mission strides, four origins, one retail run
HYPOTHESIS-ID: source-byte-writer

Session 5226 did not name the entry byte's writer. Its census base was
`0x80195190 + i*0x88` while the watches covered `0x80190E50 + i*0x88`.
Do not watch only one stride. Do not add another source-byte histogram.
Do not guard. No port rebuild.

`g_pc_hist_watch_mask` is a `uint64_t` (`tools/oracle/rs64_oracle.c`,
six sites) and `MAX_WATCHES` is 64. Eighty-two words do not fit. Before
the run, replace that mask with a bit array indexed to `MAX_WATCHES`,
raise `MAX_WATCHES` to at least 86, and rebuild only `rs64_oracle`.
A shift of a 64-bit mask by 64 or more is not a histogram. The rebuilt
binary must still print `[s5225-s0]` and `[oracle] writer-pc-phase`.

Watch index 0 stays `--watch-write 0x0:0x800000`. Then 82
`--watch-write` ranges of 4 bytes:

- watches 1..41: `0x190E70 + i*0x88`, `i=0..40` (s5225 stride)
- watches 42..82: `0x1951B0 + i*0x88`, `i=0..40` (s5226 stride)

`--pc-hist-watch` on 1..82. Keep `--watch-pc 0x8008FAAC`. Phase buckets,
colons quoted:

- `0x00690400:512`
- `0x00690800:512`
- `0x00620400:512`
- `0x00620800:512`

Same Rice video, `--secs 420`, `--hit-cap 500`, `--vi-trace --vi-poll`,
`--pc-phase-quiet`, and the s5224 Start schedule. Whole-RDRAM must reach
10000 writes. Both `0x00690400` and `0x00620400` must appear; the two
`0x..0800` siblings are the pair buffers seen in s5226 and are part of
the table even if one is absent. The census slot sum plus overflow must
equal that origin's hit count, and the 41 addresses must be exactly one
of the two strides. Lifetime `0x80090F3C` on the s5225 stride is the
histogram's positive control: s5226 counted it on all 41 of those words.

The `writer-pc-phase` rows are the retail writers. Open every reported
PC in `RecompiledFuncs` and record the store. A hit on the word is not
a hit on the byte. Only the stride the census names is evidence about
the entry byte.

Competing hypotheses:

- H-const-zero: on the live stride, across the four mission-pair
  origins, the dominant PC that stores offset `0x22` is `0x80090F3C`
  (`sb $zero, 0x22($v0)`). Retail's modal `0x00` is that constant.
  The port's `0x03` is not this store.
- H-const-one: the dominant offset-`0x22` PC is `0x80090F8C`, which
  stores the constant 1. That does not explain retail `0x00` or port
  `0x03`.
- H-other: the dominant offset-`0x22` PC is neither. Its value
  expression is the next source. Do not add a watch in this run.
- H-not-in-pair: the live stride's four phase tables have no
  offset-`0x22` PC and overflow is 0, while the lifetime control
  still shows `0x80090F3C`. The byte is not stored during the mission
  pair. The next source is an earlier phase, not another address.

Unevaluable: the whole-RDRAM control does not fire, a required mission
origin is missing, the census sum disagrees or matches neither stride,
the lifetime control PC is absent, or writer overflow drops every
offset-`0x22` PC on the live stride.
