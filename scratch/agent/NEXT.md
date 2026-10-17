# Port entry byte versus the retail constant-0 clear
HYPOTHESIS-ID: port-byte-not-retail-clear

Session 5227 named the retail writer. Do not re-watch retail. Do not
guard. The port modal `0x03` is not `sb $zero` at `0x80090F3C` and not
the constant 1 at `0x80090F8C`.

In `musyxMixActiveVoices` the entry read happens first: `jal` at
`0x80090F00` reaches `fillSampleStreamRange` (`0x8008FAAC`), and
`sb $zero, 0x22($v0)` at `0x80090F3C` runs after that call. The byte
the entry reads is the previous iteration's residue. The address
expression is `base + index*0x88`.

One port build, one run, the s5225 driver
(`scratch/agent/s5225_port_s0.sh`: same `COMMON` env, title then
hangar then mission, SIGKILL). Put the new counts in the fixup, not
in generated C. Phase-gate to `0x00690400`, `0x00690800`,
`0x00620400`, and `0x00620800`. Record only:

- at `0x80090F3C`, the destination address and a count
- at `0x80090F8C`, the destination address and the stored byte
- the existing `[s5225-s0]` census, which is the entry control

The `0x80090F3C` counter must be nonzero somewhere in the same run.
A mission-phase zero from a silent instrument is unevaluable. Both
`0x00690400` and `0x00620400` must appear. Each census with hits must
name exactly one of the two 41-address strides.

Competing hypotheses:

- H-port-misses-clear: for a mission origin, the entry `s0` values are
  absent from that origin's `0x80090F3C` destinations, and the store
  counter did fire in the run. The port does not clear the records
  the entry reads.
- H-port-clears-then-overwrites: the entry `s0` set is covered by the
  `0x80090F3C` destinations, the counts are the same order as the
  entry hits, and the entry byte is still `0x03`. The clear runs; a
  later writer puts `0x03` back before the next read. Do not add that
  writer in this run.
- H-port-address-diff: the store runs during the origin at a
  comparable count, but its destinations are the other stride, or
  neither stride.
- Unevaluable: the store counter never fires, a required origin is
  missing, or a nonempty census does not name one stride.
