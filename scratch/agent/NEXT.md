# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s660 recap (read this first)

**H-body-stomp STRUCTURAL (offline s659 dual-source):**
- fail136c reason=corrupt with 16B header restore match=1
- zero_node bad=0x801F3D30 prev=0x801F3CC0 prev_sz=0x60
- freelist walk: next = node + size + 0x10

**s660a full-body 64KB restore:**
- posctrl LIVE: snap=0x10000 node_span=0x70 next_ok=1
- recov_active=0/3 engaged (vs s659 16B recov 3/3) → body over-restore
  undoes recovery co-factor (Outcome C candidate, single-source)

**s660 product (LANDED):** mode=headers multi-header restore
- snapshot walk window 64KB, restore only 16B headers along chain
- leave body writeback intact for recovery co-factor
- banner: `mode=headers walk_cap=0x10000` LIVE
- A/B: `ROGUESQ_FL_RESTORE_MODE=body` / `ROGUESQ_FL_RESTORE_BYTES=N`

## This iteration's work unit

**Primary: consume headers freeroll (or run if not yet soaked).**

Queued: `scratch/agent/soak_queue/s660_fl_headers_restore_freeroll.sh`

If SOAK-RESULTS already has a verdict, fold it and decide A/B/C:
| ID | Claim |
|----|-------|
| H-headers-fix | headers restore → recov ≥1/3 + fail136c ~0 on thr11d + next_ok |
| H-independent-corrupt | recov ok but fail136c still ≥2/3 with next_ok=1 |
| H-headers-drought | recov drought even with headers-only → co-factor subtler |

Discriminating measurement:
1. Posctrl: banner mode=headers + restore next_ok=1 nhdr≥2 on killer
2. Freeroll product defaults BUDGET≥1200:
   - **A)** recov≥1/3 + thr11d + fail136c~0 (+ thr12/sec2?) → headers fix
   - **B)** fail136c still high with next_ok → independent corrupt
   - **C)** recov drought → need different co-factor model

Do NOT soft-skip thr12. Do NOT leave ALLOW_* on product soaks.
Keep thr11d scoring (post-hsel destroy of 0x8006F2CC).

## Do NOT
- Full-body 64KB as product (s660a drought)
- Soft-skip thr12 without recovery-active thr11d evidence
- Raise HOLD_S past 210
- Merge -385 with -387/-384/-373/-386

### Reference tags
`mode=headers`, `HIT_WRITE_RESTORE`, `fb-fl-hdr-restore`, next_ok, nhdr,
0x1F3CC0, 0x1F3D30, fail136c, thr11d_new, thr12_post, sec2_post, -414
