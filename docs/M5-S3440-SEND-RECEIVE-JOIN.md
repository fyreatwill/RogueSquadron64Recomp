# M5 Session 3440 — send/receive queue join

The independent retail oracle ran first for 120 seconds with the whole-RDRAM
positive control, both title origins, hangar driving, and a watch on
`0x80033410`. The control reached 10,000 writes; the send entry executed
169,394 times and the run reached 7,178 VI frames. In the phase-qualified
watch output, 12,534 rows used queue `0x8010FEE0`; their normalized tuple was
`(queue=0x8010FEE0, msg=0, flag=0)`.

The fresh-build port pair ran silent and Factor 5 image arms concurrently on
the validated LLE/spin-yield route. Both reached title 1024, fired the receive
positive control, and had no crash or abort markers. The phase-scoped port
send census retained 486 target-queue rows in the image arm and the same
tuple `(0x8010FEE0, 0, 0)`; the receive join retained 512 target-queue rows.
All consumed queue-head messages were zero in both arms. The first receive
join sampled a null output slot and was corrected to sample the queue's
pre-receive head entry.

This selects `H-RetailSendParity` and refutes `H-EarlierPortSendGap` at the
queue contract. The zero-valued message is not itself treated as corruption;
the next boundary is the receive consumer/output use.
