# M5 s3781 guest route-state sample

The Debug target rebuilt successfully. Before adding the port witness, the
retail oracle ran for 60 seconds with a whole-RDRAM positive control, exact
watches on the three candidate route-state bytes, and execution watches on
the S/I/L family entries. The whole-RDRAM control fired 10,003 times and the
route-state watches fired 2, 1, and 0 times, but retail remained in attract:
none of the family entry PCs executed. Retail target-phase route identity is
therefore unevaluable in this run.

The image-only port run passed 140 phase records, six family-entry controls,
title VI 1024 (`0x00790400`), and hangar VI 512 (`0x006AB400`). The new
guest-RDRAM witness emitted 257 target-phase rows (S=128, I=1, L=128), and
all rows read `state_1ad0=0x00`, `state_3b038=0x00`, and `state_1ad1=0x00`.
The pre-existing host route snapshot was inactive on all rows. This is a
single-source port result: it does not distinguish a legitimate alternate
object from a wrong route because the independent retail family phase was not
reached.

The witness only reads existing guest bytes at family entry; it does not
modify values, destinations, audio gates, or control flow.
