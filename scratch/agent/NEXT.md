# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## Single work unit

**Item -421 (rdpFs post-sec2 plateau): distinguish H-e9-not-translated from
H-e9-walker-misaligned.**

s671 (offline, on already-captured data from the -422 confirming run —
no new game run needed for this framing) scoped the existing
`[dl-sync-probe]` instrument to post-sec2 lines in
`scratch/s73_post_a_scene/s670_postsec2_pulse_2_20260811200701/run.log`
(`sec2_ln=347715`):
- 11328/29780 (~38%) post-sec2 tasks show `e9_a>0` or `e9_b>0` — the naive
  fixed-8-byte-stride tree walker (`walk_tree` in `src/main/main.cpp:739`)
  finds an 0xE9 byte value in its command walk.
- 29777/29780 (~99.99%) of the SAME post-sec2 tasks report runner
  `syncs=0` in the `[runner] task ... syncs=` line — the actual
  translated/dispatched RDP command count that drives `rdpFs`.

Two explanations, not yet distinguished:
- **H-e9-not-translated:** the guest DL genuinely contains SYNC_FULL
  requests; our translator/dispatcher drops or fails to execute them for
  this task class. Would directly explain -421's plateau as a translation
  bug — a real, fixable defect, not a content-absence dead end.
- **H-e9-walker-misaligned (check this FIRST — iron rule 5, boring before
  exotic):** `walk_tree`'s fixed 8-byte stride does not account for the F5
  ucode's variable-length inline-data commands (MoveMem 0x03 +16, TriGen
  0x05 +32, Tri 0xB4/0xBF +16 iff w0&2, TexrectGen 0xBD +16,
  SetOtherMode_*_EX 0xB3/0xBE +8 — `docs/F5-UCODE-REFERENCE.md`). An
  unaligned read after any of these commands can land mid-payload and hit
  a coincidental 0xE9 byte that is not a real opcode boundary. The
  `ROGUESQ_LOG_DL_SYNC2` walker (`src/main/main.cpp:851`, six-command-aware,
  built for the cimg-origin-desync work `-415..-417`) already implements
  the correct variable-length stride for a DIFFERENT opcode (0xFF/SETCIMG)
  — it does not currently track E9.

## Discriminating measurement

Add E9 counting to the existing `ROGUESQ_LOG_DL_SYNC2` six-command-aware
walker (`src/main/main.cpp` around line 851-931, alongside the existing
`setcimg_n`/`setcimg_wild` tracking): count `op == 0xE9` hits using the SAME
inline-data-respecting stride already implemented there
(`switch(op)` block at line 911-919), call it `e9_aligned`. Add it to the
`[dl-sync-probe2]` fprintf. This is ONE code change, one rebuild
(regen not needed — pure runtime C++, no ELF/recomp step), one instrumented
run carrying both `ROGUESQ_LOG_DL_SYNC=1` (existing) and
`ROGUESQ_LOG_DL_SYNC2=1` (already exists as a flag, just not included in
`GAME_EXTRA_ENV_BASE` in `scratch/agent/s670_postsec2_pulse_freeroll.sh` —
add it there) so both counts land in the same run and are directly
comparable per-task (match by task number `s_n`/`#N`).

Reuse `scratch/agent/s670_postsec2_pulse_freeroll.sh` unmodified except for
the env line; same recipe (`BUDGET_S=2400`, in-session only — NOT
soak-queueable, same reasoning as -422: single successful attempt needs
~1400-2000s wall). Do not target `TARGET_PULSED` this time (that variable
is -422-specific and now irrelevant — item is CLOSED); just need ONE
recovery-active, sec2-reached attempt with a few hundred post-sec2 tasks
logged, which the existing engage/recovery retry loop already gets you.

## Outcomes

- **A)** `e9_aligned` stays ~0 across the post-sec2 tasks that had nonzero
  naive `e9_a`/`e9_b` → **H-e9-walker-misaligned CONFIRMED**; the 38% hit
  rate was a fixed-stride artifact. -421 residual reopens to "why is
  runner syncs=0" with E9-presence ruled out as the guest-content
  explanation — next probe becomes runner-side (does the translator see
  ANY E9 opcode at all in properly-decoded commands feeding into `syncs`,
  or is the mission genuinely sync-free and rdpFs advances by some other
  mechanism we haven't identified).
- **B)** `e9_aligned` tracks close to the naive `e9_a`/`e9_b` (E9 really is
  present at real command boundaries in a large fraction of post-sec2
  tasks) → **H-e9-not-translated CONFIRMED**; promotes to a real, high-value
  lead. Next: find the runner code path that turns a decoded 0xE9 opcode
  into a `syncs++`/`rdpFs` increment and instrument why it's not firing for
  these specific tasks (task flags? command-buffer offset heuristic
  mismatch? a guard added in one of the -3xx/-4xx freelist-era product
  changes silently swallowing this opcode class?).
- **C)** Mixed/inconclusive (some tasks confirm, some refute) → note the
  split by task shape (tris count, cmds_a/cmds_b, end_a/end_b) and treat as
  two sub-populations, not a single verdict.

## Do NOT

- Re-run or productize the -422 input pulse (CLOSED, dual-source
  CONFIRMED, no residual — see `docs/CURRENT-TRUTH.md` item -422 and
  `PORTING-STATE.md` Sessions 670-671).
- Re-soak thr11d multi-hold rate (-419 CLOSED).
- Chase packTlut SIGBUS (-373) until the loader actually fires (still 0).
- Productize `DROP_GARBAGE_CIMG` (s666 REJECTED).
- Spend more than 3 consecutive iterations on this E9-alignment question
  without a discriminating result before pivoting per iron rule 8 — this is
  iteration 1 on this specific sub-question (the `m3-post-exit-fs-stall`
  slug's cumulative age is much longer, but the E9-alignment framing is
  new as of s671).
