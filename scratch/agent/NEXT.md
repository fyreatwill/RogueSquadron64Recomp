# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s583 recap (read this first)

| Observation | Implication |
|-------------|-------------|
| `[rdp-fullsync]` positive control | hangar 0x7778C8 b0=E9 size=8 |
| Dual B: 238 singles @ **0x76DF60** = 238 syncs=1 | H-sync4 **source FOUND** |
| All singles b0=E9 w0=E9000000 size=8 | H4b/H4d REFUTED; not synthetic |
| e9_b=0 on dual DLs, E9 at fixed side-slot | H4c side-slot CONFIRMED |
| After last single: 0 submits; sticky E9→E7→FD | stop edge open → item -353 |

Authoritative: live `[rdp-fullsync] kind=single` (not sticky `fs_addr` alone).

## This iteration's work unit

**H-sync4 stop edge: who owns phys 0x76DF60, and why 8-byte FULL_SYNC submits die.**

### Hypotheses
- H5a: LLE DPC-submits a fixed RDP/output slot at 0x76DF60; guest overwrites the
  E9 when cutscene phase advances (byte mutates → no more op family match).
- H5b: LLE path that reaches the slot is gated (halt/yield/task flags); slot may
  still hold E9 for a while but is no longer submitted.
- H5c: Dual-buffer flip retires the producer that was emitting the side-slot E9
  (different OSTask/data_ptr family after task ~5491).
- H5d: Address is inside one of the dual DL regions via a non-tree link the e9_b
  walker misses — linear/range check from 0x729690/0x747930 still failed offline
  (delta 0x448d0 / 0x26630); re-verify with live dump of ±0x40 around the slot.

### Discriminating measurement (same-run, one build)
1. Arm `ROGUESQ_LOG_RDP_FULLSYNC=1` + `ROGUESQ_LOG_DL_SYNC=1` (already land).
2. Add **one** of: (preferred) write-watch / log on stores into phys 0x76DF60
   (host-side if guest writer unknown), **or** dump 16 bytes at 0x76DF60 on every
   dual-DL task boundary (runner) for 20 tasks before + 20 after last single.
3. Correlate last single n with dual task #, data_ptr, and slot bytes.
4. Outcomes:
   - Slot E9→non-E9 **before** last submit → H5a (content kills match)
   - Slot still E9 after last submit for N tasks → H5b (path stops submitting)
   - data_ptr/OSTask family changes at edge → H5c
   - Slot is linked from dual DL via unfollowed op → H5d (extend walker)

### Exact commands
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# After adding slot dump / write watch + rebuild:
env PROBE_MODE=start_only HOLD_S=45 \
  ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
  GAME_EXTRA_ENV="ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_FORCE_CASE5_START=40 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_FS_SLOT=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s584_hsync4_slot 5 12
```

### Do NOT
- Re-litigate H-sync1/2 or treat hist-only without kind=single.
- Chase leave-path crashes or item -347 until 3rd occ (s583 crash was 0x80065e94 —
  different; file if recurs).
- Reopen s178 / thr-resume-skip.
- Use natural double_start as sole vehicle (leave-path crashy).
