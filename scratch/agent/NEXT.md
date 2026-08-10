# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s604 recap (read this first)

Folded `s603_item338_item361_hold180` (336s, rc=2): **no scored attempt**
(not A–F). 2/2 pre-engagement deaths at hangar state=5 (hangarbay n≈1000,
0 ACE80): A1 item -306 `0x800aafa8`; A2 host Metal `0x800ab0e0`.

**Root cause of 0 engagement:** recipe `NEED=HOLD_S+90=270` refused attempt 3
after 2×~170s path deaths (remain≈220). s602 r3 needed attempt 4 under a 30s
start floor. Not an engagement-rate regression (s602 r3 engaged no-sticks).

Queued `s604_item338_item361_hold180_budgetfix.sh`: HOLD_S=180,
`START_FLOOR_S=100`, BUDGET_S=580, MAX_ATTEMPTS=8, same dual-target gate.

Full: CURRENT-TRUTH -369/-361; PORTING-STATE Session 604.

## This iteration's work unit

**Fold in the `s604_item338_item361_hold180_budgetfix` soak result and act.**

1. Read SOAK-RESULTS.md line + scored-attempt gate (if any):
   `beginframe_s0_guard`, `thr11_destroy`, `sec4_post`, `inject_max_n`,
   `recov76B768`, `coalesce_guard2_r2`, `crash`, `crash_pc`, `class_hint`,
   and attempt count / engagement flag.
2. Classify:
   - **A** `beginframe_s0_guard>=1` + no `0x8000afa0` → -338 confirm 1/2; queue 2nd.
   - **B** `thr11_destroy=1` + `sec4_post>=1` + `coalesce_guard2_r2>=1` + no
     crash at `0x8000247c` → -361 confirm 1/2; queue 2nd.
   - **C** thr11 destroy + sec4_post + crash `0x8000247c` + 0 r2 guard → R2 miss.
   - **D** thr11 destroy + sec4_post + other crash → file breadcrumb.
   - **E** thr11_destroy=0 at HOLD end → pivot recovery-cell (H-recov*); do NOT
     raise HOLD_S past 210.
   - **F** 0 beginframe, thr11 live, no afa0, crash=ok → park -338 passive; E pivot.
   - **G** rc=2 again **and** ≥4 attempts tried → engagement collapse independent
     of budget; pivot force-write hangar state=6 under FORCE_CASE6_START after N
     case5 frames (s602 E path).
   - **G'** rc=2 with <4 attempts (budget still tight / early deaths) → recheck
     START_FLOOR math once; do not treat as engagement collapse.
3. If B or A: queue one confirm soak only.

## Hypotheses for E/F pivot (only after a scored E or F)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-recov1 | Recovery cell `0x76B768` required for cutscene advance that stops thr-11 | thr11_destroy rate: recov>0 vs recov=0 at equal HOLD |
| H-recov2 | Inject mode-1 never promotes guest FULL_SYNC into recovery cell | Instrument guest E9 landing at 0x76B768 under inject |
| H-time | 180s still short vs cutscene length variance | Only if thr11_destroy seen ≥1× under 180 |

## Do NOT
- Raise HOLD_S past 210.
- Re-characterize -338 from the 5 historical logs (done s600).
- Chase `waitForAnyAudioSlot+244` (item -362) or item -306 deep-hangar recurrence
  as a new single-crash guard (M3 = idiom-class audits only).
- Treat thr495FC_creates as post-exit thr-12 (boot-only).
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Re-arm default stick schedule (no-sticks works when ACE80 settles).

### Reference tags
`[beginframe-s0-guard]`, `[case6-force-start]`, `[hangar-sel]`,
`[state-write] site=0x800ACE80`, `[buttons-hangar] site=0x800ACE94`,
`[thr-create]`/`[thr-destroy]` entry=`0x8006F2CC`,
`[rdp-fullsync] ... addr=0x0076B768`, `[fs-pipe-inject]`,
`[overlay] start-match: section 4`, `[coalesce-heap-r2-guard]`,
`[CRASH][last-guest-pc]` / `[CRASH][pc-symbol]`.
