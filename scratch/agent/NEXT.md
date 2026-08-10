# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s621 recap (read this first)

**s620 freeroll bug fixed; -385 M1 still PENDING (class-D not re-entered).**

### s620 soak fold
- recovery_silent; crash trackResourceListWithMappingTables+1228 / 0x80065e94
- Freeroll required EARLY_REASON=recovery_silent → wrongly scored silent crash

### Freeroll fix (H-freeroll1 CONFIRMED)
- Any eng+hsel with recov768=0 freerolls (drop EARLY_REASON gate)
- s621b positive control: silent_n=2 freerolls, no false score

### s621 recovery-active scored
- force6 old=5→6 recov768=7952 BASE_CTRL_PASS
- thr11c_post=1 thr11d_new=0 sec4_post=0 cshadow=0 ltex=0 **ltexmg=0**
- Abort: sinfApprox NAN_CHECK (funcs_5.c:6460) ← buildPositionAndCallTransformHelper
  ← runModelViewerLoop — residual **-386** (1× freeroll; known s214 family)

### s621b budget exhaust
- 2× recovery_silent freeroll (trackResourceList); no recovery-active in 560s

Full: CURRENT-TRUTH -386/-385; PORTING-STATE Session 621.

## This iteration's work unit

**Live-verify level-tex-malloc-guard on recovery-active class-D (retry with freerolls).**

1. Use recipe with freerolls: recovery_silent (recov768=0 any EARLY), mat3inv,
   scenegraph/readacct/matfree 1st, **sinfApprox 1st** (-386).
2. BUDGET_S=560 ok; if silent-heavy, prefer freeroll early-kill mid-run for
   trackResourceList (si_addr 0x38000000c + trackResourceList) to free budget
   faster — optional.
3. Require BASE_CTRL_PASS + recovery-active scored.
4. Prefer post-hsel metrics: thr11d_new, sec4_post, thr12_post, cshadow_*,
   ltex, **ltexmg**, ltex_null, ship_*, scenegraph, readacct, matfree, sinfapprox
5. Classify:
   - **M1** ltexmg≥1 ∧ ltex_null=0 → guard LIVE-VERIFIED (-385)
   - **M2** ltex_null=1 → guard miss / binary stale
   - **M1+thr12** unexpected if soft-skip before registerServiceWorker
   - **I2** thr11 live + sinfApprox 2nd on scored → escalate -386
   - **G** thr11d_new+sec4+cshadow thr12=0 ltexmg=0 — class-D without null path
   - **E** recovery_silent freeroll
6. If M1 and thr12=0: next unit is **why rs_malloc(0x136C) null** (heap free
   head / size log with positive control) — do not soft-skip thr12 create.
7. Do NOT raise HOLD_S past 210. Do NOT remove state==5 gate.
8. Do NOT merge -385 with -384/-373/-386.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-freeroll1 | (CONFIRMED s621b) recov768=0 freerolls without EARLY | — |
| H-ltexmg1 | null-malloc guard LIVE on class-D | ltexmg≥1 on scored class-D |
| H-ltexOOM | rs_malloc null = heap pressure | free-head / size (after M1) |
| H-sinf1 | (1× freeroll) sinfApprox Abort noise | 2nd thr11-live → escalate -386 |
| H-matfree1 | SUPPORTED | 0 more matfree scored |
| H-thr11d1 | CONFIRMED s619 | thr11d_new under force6+recov |
| H-recov1 | SUPPORTED | thr11d/sec2 requires 76B768 |

## Do NOT
- uint32 KSEG0 MEM bases
- Remove state==5 FORCE_STATE6 gate
- Raise HOLD_S past 210
- Soft-skip thr12 without fixing null alloc
- Merge -385 with -384/-373/-386
- Leave FORCE tools default-ON
- Trust thr11d_post without thr11d_new

### Reference tags
`[level-tex-malloc-guard]`, `ltexmg`, `sinfApprox`, `NAN_CHECK`,
`trackResourceListWithMappingTables`, `0x80065e94`, `0x80048248`,
`thr11d_new`, `0x76B768`, H-freeroll1
