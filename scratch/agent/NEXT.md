# Next work unit (s4501): M3 jal-rs_free class-closure tally

HYPOTHESIS-ID: m3-idiom-class-audit

Goal: decide whether the `jal rs_free` class is closed. Enumerate every
word `0x0C000726` in ROM vram `0x80000400..0x8010B6D0` (offset
`vram - 0x7FFFF400`; menu/cinematic overlays share addresses with the
mission image, so also scan their ROM ranges if CURRENT-TRUTH/PROJECT-OVERVIEW
give them). Control first: hits at 0x800F9F94, 0x800EED50, 0x800EC564,
0x8007BE50, 0x80100F84, 0x80100F90 or the scan is invalid. Use system
`python3` (`.venv-splat` is not allowlisted headless); `scratch/agent/s4500_dis.py`
is a mini decoder.

Map each hit to an audit doc: `grep -l 0xADDR docs/M3-S44*.md docs/M3-S45*.md`
(hex lowercase and uppercase). Output a table in
`docs/M3-S4501-RS-FREE-CLASS-CLOSURE-TALLY.md`.

Hypotheses: H-Closed (every site has an audit doc with a verdict);
H-Residual (named unaudited sites -> they become the next units, one per
session); H-Unevaluable (overlay ranges not determinable).
Discriminator: count of hits with no doc. Zero -> Closed (then pivot to
the M5 de-stub plan or the rename sweep per the iteration contract).
No runtime run.
