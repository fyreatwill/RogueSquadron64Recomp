# Next: name the writer of the mission-entry source byte
HYPOTHESIS-ID: source-byte-writer

Session 5224 closed the frequency question. Do not add another histogram.
Do not guard. Do not resume the rename sweep. Do not rename `bzero_recomp`
or `bcmp_recomp`.

Retail, every hit at `0x8008FAAC` on the mission origins: modal `0x00`
(119949/121195 and 126435/127740), `0x03` count 0. Port, same site: modal
`0x03` (79212/79362 and 79385/79498). s5223's first three samples had `s0`
in {`0x80195190`, `0x80190E50`}, so the candidate bytes are physical
`0x191072` and `0x1951B2`. Those samples are not a census.

One port build and one retail oracle run. Add the census and the retail
write watches before either run. macOS has no `ROGUESQ_HWBP`; do not use it.

Both sides, in the existing s5224 hooks: a 64-slot table of `s0` per
mission origin (address, count, overflow). Port flushes it on the leave
line as one line. Retail prints it at shutdown. Positive control: the slot
counts plus overflow equal that origin's entry/hit count.

Retail write watches, armed at first VI, not at the first entry (the byte
may be stored once before the first read):

- `--watch-write 0x191070:0x191074`
- `--watch-write 0x1951B0:0x1951B4`
- `--pc-hist-watch` on each of those watches
- `--pc-hist-phase 0x00690400:512` and `0x00620400:512`
- whole-RDRAM watch stays index 0

The `writer-pc-phase` rows are the retail writers of those words. In the
same iteration, open the recompiled store at each reported PC and record
the value expression. That is the port-side half: there is no macOS store
hook, so the generated store is the port witness.

Competing hypotheses:

- H-same-writer-different-value: the modal `s0+0x22` is inside a watched
  word, and the retail writer PC's generated store is reached with a source
  that is `0x00` on retail and can be `0x03` on the port. Next question is
  that source, not another address.
- H-different-writer: the modal address is watched, but the generated store
  at the retail writer PC is absent, neutralized, or not on the port path
  that produces `0x03`.
- H-wrong-candidate: the modal `s0+0x22` is outside both watched words.
  The writer-pc table is then unevaluable. The census addresses are the
  next watch list. Do not add a third watch in this run.

Unevaluable: census slot counts disagree with the entry count, the
whole-RDRAM control does not fire, or a mission origin is missing.
