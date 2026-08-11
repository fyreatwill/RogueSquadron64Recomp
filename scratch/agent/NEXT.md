# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s659 recap (read this first)

**Outcome A CONFIRMED dual-source (product freelist-header restore LIVE):**

Product path (default ON, no ALLOW_*):
- policy A: wild freelist-range → ALLOW_WILD_FL + HIT_WRITE_RESTORE
- non-freelist wild still SKIP_WILD_W
- freeroll: recov 3/3 engaged; thr11d_new 3/3; fail136c 2/3 reason=corrupt
- classic killer restore match=1; heartbeats 0x2/0x60 to ~245s
- thr12_post=0 sec2_post=0 (class-D still blocks)

s658 ALLOW restore had thr11d_new=0/3; product reopens thr11d 3/3 with
header intact. fail136c residual with restored header → freelist **body**
beyond 16B still stomped by wild CIMG, or independent corrupt path.

## This iteration's work unit

**Primary: class-D / fail136c residual under product header restore.**

Hypotheses:
| ID | Claim |
|----|-------|
| H-body-stomp | wild CIMG stomps freelist node body past 16B header → reason=corrupt |
| H-independent-corrupt | fail136c corrupt independent of freelist writeback |
| H-mid-race | fail136c samples freelist during mid-write zero window |

Discriminating measurement (one build, one freeroll):
1. Expand product restore from 16B header to full freelist node (size field
   0x60 = 96B, or fixed 0x60 from header size) — OR hole-punch freelist
   range out of writeback memcpy (skip writing [hdr, hdr+node_size) entirely
   while still "completing" writeback for recovery co-factor).
2. Posctrl: product banner + restore_ok on killer.
3. Freeroll product defaults BUDGET≥1200:
   - **A)** fail136c drops to ~0 on thr11d recovery-active + thr12/sec2 may
     advance → body-stomp was residual
   - **B)** fail136c still 2/3+ with expanded restore → independent corrupt
   - **C)** recov drought returns → writeback co-factor needs full freelist-
     range bytes written (not just "completion")

Prefer hole-punch or expand-restore over soft-skip thr12. Do NOT leave
ALLOW_* on product soaks. Keep thr11d scoring (post-hsel destroy of
0x8006F2CC).

## Do NOT
- Soft-skip thr12 without recovery-active thr11d evidence
- Raise HOLD_S past 210
- Revert product restore without dual-source regression
- Merge -385 with -387/-384/-373/-386

### Reference tags
`ALLOW_WILD_FL`, `HIT_WRITE_RESTORE`, `fb-fl-hdr-restore`, 0x1F3CC0,
0x1F0D74, fail136c, thr11d_new, thr12_post, sec2_post, -413, -408
