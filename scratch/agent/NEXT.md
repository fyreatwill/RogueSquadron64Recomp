# Next: writer PCs of the retail mission-entry bytes
HYPOTHESIS-ID: source-byte-writer

Session 5225 selected H-wrong-candidate. Do not watch `0x191070` or
`0x1951B0` again. Do not add another source-byte histogram. Do not guard.
Do not resume the rename sweep.

Retail mission `s0` is `0x80190E50 + i*0x88` for `i=0..40`. The byte at
`s0+0x22` is physical `0x190E72 + i*0x88`. The aligned word is
`0x190E70 + i*0x88`. One retail oracle run. No port rebuild. macOS has no
`ROGUESQ_HWBP`.

Watch index 0 stays `--watch-write 0x0:0x800000`. Then 41
`--watch-write` ranges, `0x190E70+i*0x88` for 4 bytes, `i=0..40`.
`--pc-hist-watch` on each of those 41 indices (1..41). Keep
`--watch-pc 0x8008FAAC` so the existing s5225 census still prints, and
keep both `--pc-hist-phase` buckets `0x00690400:512` and `0x00620400:512`
(quote the colon; zsh history expansion splits `:512`). Same Rice video,
`--secs 420`, `--hit-cap 500`, `--vi-trace --vi-poll`, `--pc-phase-quiet`,
and the s5224 Start schedule. Whole-RDRAM must reach 10000 writes, and
both mission origins must appear. The census slot sum plus overflow must
equal that origin's hit count.

The `writer-pc-phase` rows are the retail writers of those words. Open
every reported PC in `RecompiledFuncs` and record the store. A hit on the
word is not a hit on the byte: offsets `0x20` and `0x21` share it.

Competing hypotheses:

- H-const-zero: during both mission origins the dominant PC that stores
  offset `0x22` is `0x80090F3C` (`sb $zero, 0x22($v0)`, `v0 = base +
  index*0x88`). Retail's modal `0x00` is that constant. The port's `0x03`
  is not this store.
- H-const-one: the dominant offset-`0x22` PC is `0x80090F8C`, which stores
  the constant 1. That does not explain retail `0x00` or port `0x03`.
- H-other: the dominant offset-`0x22` PC is neither. Its value expression
  is the next source. Do not add a watch in this run.

Unevaluable: the whole-RDRAM control does not fire, a mission origin is
missing, the census sum disagrees with the hit count, or writer overflow
drops every offset-`0x22` PC.
