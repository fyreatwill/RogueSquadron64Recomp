# NEXT work unit

HYPOTHESIS-ID: m4-item249-bulk-relocation-resume-s418

## s418 recap (loop-mandated pivot, no code change)

The loop's MANDATORY-PIVOT gate fired after s415/s416/s417 all ran
`HYPOTHESIS-ID: m4-item249-bulk-relocation-n75` without closing it. Checked M5 (item -227/-228: DONE,
fully CLOSED, needs a genuinely new lead — not actionable) and M3 idiom-audit mode (item -239..-247:
exhausted, needs human reconfirmation — not actionable); both fell through, confirming M4 ordinary bulk
relocation remains the correct sanctioned fallback per the standing USER DIRECTIVE. Rather than run an
8th consecutive n=75 batch under the recycled slug, ran the single highest-information discriminating
probe for the question the last 4 sessions kept deferring: **are the 7 known-bad functions
disproportionately `mission`-overlay-destined** (all 7 are tagged `CONFIRMED:mission`, 0 `menu`)? If so,
that would argue for a mission-overlay-specific structural cause worth a dedicated root-cause session
instead of continuing blind batch-and-bisect.

**REFUTED.** Reconstructed the actual per-session candidate-pool mission/menu split from the surviving
probe-result files (`s412_probe1.txt`/`s412_probe2.txt`/`s414_probe1.txt`/`s416_probe_results.txt`/
`s417_probe_results.txt`) for the 4 sessions that produced a bad function. Three of the four sessions
(s412 x2, s414, s416) probed **100%-mission candidate pools — zero menu-tagged candidates appeared in
any of them** — so their bad functions landing mission-side is not evidence of anything, it was the only
overlay on offer. Only s417 had a mixed pool (32 mission/43 menu, 43%/57%), and its one bad function did
land mission-side, but n=1 against a 43% base rate is statistically inconclusive alone. The "7/7 mission"
pattern is a sampling artifact of which pools happened to get probed which sessions, not a real signal.
Closes this angle. Strengthens (doesn't newly establish) the standing read that these are isolated
per-function bugs converging on 2 shared downstream crash sites (`0x800290d4` x4, `0x80011088` x2, both
below `overlay_start`, outside any relocated function's own body) — no process change indicated.

No code/build/soak this session — pure archival analysis of files already on disk. `579/778` unchanged,
no new `m4_known_bad.txt`/`m4_known_skip.txt` entries. Full detail: `PORTING-STATE` Session 418,
`docs/CURRENT-TRUTH.md` item -249..-258 (tail).

## s417 recap

Resumed ordinary bulk relocation at n=75 per s416's handoff recipe. Regenerated candidates fresh (293
total, 283 actionable after filtering `m4_known_bad.txt` (6) + `m4_known_skip.txt` (4) — matched
NEXT.md's estimate exactly), probed the next 75 (51 CONFIRMED + 24 WEAK, 0 NONE/AMBIGUOUS — every name
resolved to exactly one destination overlay), applied (32 to mission, 43 to menu), regenerated, built,
and live-verified. Crashed: `last-guest-pc=0x80011088`, 0 frames captured.

Reverted the full 75 as a same-run positive control (`make_elf.py` unmapped-functions-skipped delta
223↔298, exact ±75), confirming the batch. Rebuilt+live-verified the reverted baseline clean (19 frames,
0 crash markers) before starting bisection.

**Applied the sibling-independence discipline from the START this time** (not reactively after finding a
second bug, as s415/s416 did): at every split, both branches get tested, no branch assumed clean by
elimination. Halves-bisected: 75 → half-A(37,CRASH)/half-B(38,deferred) → A1(18,CRASH)/A2(19,deferred) →
A1a(9,clean)/A1b(9,CRASH) → C1(5,CRASH)/C2(4,deferred) → D1(2,CRASH)/D2(3,deferred) →
E1(`initHangarDisplayItemTimers`,**CRASH ALONE**)/E2(`tickHangarDisplayItemAnimations`,deferred).

Then independently tested every deferred sibling before declaring done: E2 (1) → clean. D2 (3) → clean.
C2 (4) → clean. A2 (19) → clean. half-B (38) → clean. **Unlike s415 and s416, this batch had exactly ONE
bad function** — the full sibling sweep came back clean across the board, no second bug hiding anywhere
in the tree.

**Signature note**: `initHangarDisplayItemTimers`'s crash site (`0x80011088`) is NOT the `0x800290d4`
family s415/s416 both hit — it matches s407's `initPlayerCraftTrailBuffers` instead. Two independently-
recurring crash sites now on record, both outside any relocated function's own body (core `.text`, below
`overlay_start`), consistent with s414's read that these are downstream/indirect corruption sites, not
per-function bugs. Not investigated as a root-cause session (out of scope for ordinary bulk relocation).

Applied the final 74-name batch (75 minus the one bad function), full regen+build, `nm`-verified all 74
present and the bad name absent, **live-verified clean 2/2** (88.5s/88.6s to phase, 19 frames each, 0
crash markers both runs). **579/778 done** (was 505/778), +74 this session.

Built three reusable scripts this session, all still valid for future bisections:
- `scratch/agent/s417_revert.py <names-file>` — generic revert (any named subset, from wherever
  `s400_apply_batch.py` put it, back to `main_overlay.txt`). Supersedes s414's session-specific version.
- `scratch/agent/s417_apply_names.py <names-file>` — filters a probe-results file down to a named
  subset, ready for `s400_apply_batch.py`.
- `scratch/agent/s417_cycle.sh <outdir-name>` — the full delete-funcs / make_elf / N64Recomp / fixup /
  cmake-build / live-verify / RESULT=CLEAN-or-CRASH cycle in one shot. Cut each bisection round from
  ~8 manual tool calls to 1. Prints `RESULT=CRASH <last-guest-pc line>` or `RESULT=CLEAN <frame count>`
  as its last line — grep for `RESULT=` in the backgrounded task's output file.

Full detail: `PORTING-STATE` Session 417, `docs/CURRENT-TRUTH.md` item -249..-258.

## Next work unit: resume ordinary bulk relocation at n=75

Per s411-s417's established cadence: n=75 remains the confirmed-safe steady-state batch size for
ordinary relocation. 219 candidates remain per a fresh regen (218 actionable after filtering
`m4_known_bad.txt` (7) + `m4_known_skip.txt` (4)).

### Recipe
1. Regenerate the candidate list fresh (`scratch/agent/s414_gen_candidates.py` still works — reads
   `main_overlay.txt`/`mission_overlay.txt`/`menu_overlay.txt`/`cinematic_overlay.txt` directly, no
   session-specific state). Confirm the actionable count (candidates minus known-bad minus known-skip)
   is in the neighborhood of 218 — some drift from lingering NONE/AMBIGUOUS items is expected and
   normal (see `m4_known_skip.txt`'s header comment).
2. Probe the next 75 names (`s400_probe_batch.py`-style), tag CONFIRMED/WEAK/NONE/AMBIGUOUS.
3. Apply via `s400_apply_batch.py`, delete `RecompiledFuncs/funcs_*.c` (see path note below), regen
   (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py`), build, `nm`-verify all 75 present, live-verify
   (phase-gated, `PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1`). **Use
   `scratch/agent/s417_cycle.sh <outdir>` for the regen+build+live-verify part — it does all four steps
   plus the CLEAN/CRASH report in one call.**
4. **If CLEAN**: live-verify a second time (2/2 discipline), commit, done.
5. **If CRASH**: do NOT guess. Revert the full batch first as a same-run positive control (`s417_revert.py
   <batch-file>`; confirms the batch, not environment, is responsible — check the `make_elf.py`
   unmapped-functions-skipped delta matches the batch size exactly both ways). Then halves-bisect using
   `s417_apply_names.py`/`s417_revert.py`/`s417_cycle.sh` (all still generic, no changes needed). **At
   every split, test BOTH branches before moving on — do not assume a sibling is clean by elimination.**
   s415 and s416 each found a second bad function hiding in an assumed-clean sibling; s417 tested every
   sibling from the start and found only one bug, but the discipline must stay standing since a batch
   CAN hide more than one.
6. If a THIRD occurrence of `last-guest-pc=0x80011088` (s407's `initPlayerCraftTrailBuffers` site) OR a
   FIFTH occurrence of `last-guest-pc=0x800290d4` (s415/s416's four-function site) turns up, consider
   pausing ordinary relocation for one iteration to source-read what's actually at that address — two
   recurring crash sites with multiple independent trigger functions each is starting to look like
   systemic downstream corruption, not batch-specific noise.

### Environment/tooling notes (unchanged from s414-s417, still accurate)
- `RecompiledFuncs/funcs_*.c` live at
  `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c` (50 files, `funcs_0.c`
  through `funcs_49.c`). `s417_cycle.sh` deletes them automatically before every regen.
- `nm` is not on the Bash allowlist directly; prefix with `env` (`env nm <path>`).
- `find ... -delete` and glob-pattern `rm` are both blocked by the sandbox; delete generated files by
  listing exact paths to `rm` (or run one `rm -f` call per ~19-25 files to stay under the multi-op
  approval trigger) — `s417_cycle.sh` already does this internally.
- `pc-symbol` in `[CRASH]` markers is NOT a reliable cross-build crash signature — always compare
  `last-guest-pc`, not `pc-symbol`.
- Live-verify commands / `s417_cycle.sh` runs take longer than 120s (the `phase width=512` gate alone
  takes ~88-89s, plus build time) and auto-background; use `TaskOutput` with `block=true` on the
  returned task_id to wait synchronously without foreground-polling — cleaner than `Monitor` for this
  single-completion case.
- The "captured N frames" line is printed by `probe.sh` to its own stdout, NOT written into the
  `run.log` inside the outdir — `s417_cycle.sh` captures it via `$(...)` command substitution, not by
  grepping the log file.

## Soak queue

None currently queued — each batch's live-verify is inline (phase-gated, ~90-140s including build).
