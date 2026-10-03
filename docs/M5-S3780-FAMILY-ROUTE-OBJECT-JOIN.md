# M5 s3780 family route/object join

The Debug target rebuilt successfully. The image-only/oracle capture passed the
oracle whole-RDRAM positive control, all six family-store controls, title
`1024 @ 0x00790400`, and hangar `512 @ 0x006AB400`. S/I/L entry controls
produced 257 target-phase rows (S=128, I=1, L=128), all with `target_arg=0`.
Family stores remained outside the target ranges and clear object: 768 title
rows had `clear_obj=0x80178C80`, and 512 hangar rows had
`clear_obj=0x801797B0`; all had `target=0`, `clear_exact=0`, and
`clear_span=0`.

The entry and destination measurements refute H3 (target-relevant entry
arguments transformed into alternate destinations) for this capture. The
route snapshot was inactive on every row (`active=0`, ordinal and row
`0xFFFFFFFF`, arm `n/a`), so it cannot distinguish H1 (legitimate alternate
object) from H2 (wrong route/overlay state). This is single-capture evidence;
the next discriminator must obtain route identity independently of the
inactive audio-route snapshot. No game value, destination, audio gate, or
control flow was changed.
