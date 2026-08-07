# NEXT work unit

HYPOTHESIS-ID: m4-item249-bulk-relocation-n75

## s420 recap

Resumed ordinary bulk relocation at n=75 per s417/s418/s419's handoff. Regenerated candidates fresh
(146 total, 133 actionable after filtering `m4_known_bad.txt` (9) + `m4_known_skip.txt` (4) by exact
first-field match) — higher than the stale ~126/117 estimate in the prior NEXT.md; the docs' running
subtraction arithmetic has drifted from the true regenerated count before (s404) and isn't
authoritative — always trust a fresh regen over the doc estimate.

Probed the next 75 names (`s400_probe_batch.py` → `scratch/agent/s420_probe1.txt`): 57 CONFIRMED + 18
WEAK, 0 NONE/AMBIGUOUS. Applied via `s400_apply_batch.py` (54 → `menu_overlay.txt`, 21 →
`cinematic_overlay.txt`). Ran the full cycle (`s417_cycle.sh s420_batch1_verify1`): regen → N64Recomp
→ fixup → build → live-verify. **Clean on the first try** — 88.3s to phase, 20 frames, 0 `[CRASH]`
markers. Second independent live-verify (`s420_batch1_verify2`, 2/2 discipline): also clean, 88.7s, 20
frames, 0 crash markers. Both logs also checked for `[missing-func]`: 0/0.

No bisection needed — the first fully-clean 75-batch since s413's ordinary-resumption era (s414, s416,
s417, s419 each hit a crash requiring bisection). Nothing added to `m4_known_bad.txt` or
`m4_known_skip.txt` this session.

**727/778 done** (was 652/778), +75 this session. Remaining per this session's fresh regen: 71 names
still in `main_overlay.txt` (58 actionable, 13 permanently excluded: 9 known-bad + 4 known-skip).

`0x800290d4`'s trigger-function count is unchanged at 5 (`allocObjectPoolNode`,
`tickCraftMountedAnimationEffect`, `stepObjectOrientationTowardTarget`, `updateHudHealthIndicator`,
`buildFormatMessageGlyphBuffer`) — no crash this session to add a 6th. The s419 flag (pause and
source-read `0x800290d4` if a 6th trigger turns up) still stands, unchanged.

## Next work unit: resume ordinary bulk relocation at n=75

Per s411-s420's established cadence: n=75 remains the confirmed-safe steady-state batch size. ~58
actionable candidates remain per s420's fresh regen — **this is close to exhausting the batch-sized
supply**: one more n=75 batch (or two smaller ones) may finish the ~801-803-function phantom-overlay
family entirely. Budget this session's planning around that: if the actionable count comes back near or
below 75, take the WHOLE remaining actionable set as one batch rather than an artificial 75-cap split,
and be prepared for the item to close this session or next.

### Recipe (unchanged from s417-s420, all tooling still generic and reusable)
1. Regenerate the candidate list fresh (`python3 scratch/agent/s414_gen_candidates.py` — reads
   `main_overlay.txt`/`mission_overlay.txt`/`menu_overlay.txt`/`cinematic_overlay.txt` directly, no
   session-specific state; writes `scratch/agent/s414_candidates_all.txt`). Filter out
   `m4_known_bad.txt` + `m4_known_skip.txt` by exact name match (first whitespace-delimited field, not
   substring — comment lines can contain a bad-function's name as a false positive, see s419's
   `getStructField0xC` near-miss) to get the actionable list. Expect ~58, not the stale 126/117 figures
   from older NEXT.md revisions — always trust the fresh regen.
2. Probe the next batch (up to 75, or the whole remainder if <=75) via `scratch/agent/s400_probe_batch.py`,
   tag CONFIRMED/WEAK/NONE/AMBIGUOUS.
3. Apply via `scratch/agent/s400_apply_batch.py`, then run `scratch/agent/s417_cycle.sh <outdir>` — it
   deletes `RecompiledFuncs/funcs_*.c`, runs make_elf.py → N64Recomp → fixup_game_funcs.py → cmake
   build → live-verify (phase-gated, `PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180
   PROBE_LEAVE_OK=1`), and prints `RESULT=CLEAN <frames>` or `RESULT=CRASH <last-guest-pc line>` as its
   last line.
4. **If CLEAN**: live-verify a second time (2/2 discipline, plain `probe.sh` invocation with a different
   outdir name is fine — no need to re-run the whole cycle script, just the live-verify tail), commit,
   done.
5. **If CRASH**: do NOT guess. Revert the full batch first as a same-run positive control
   (`scratch/agent/s417_revert.py <batch-file>`; confirms the batch, not environment, is responsible —
   check the `make_elf.py` unmapped-functions-skipped delta matches the batch size exactly both ways).
   Then halves-bisect. Write a small session-local `sNNN_apply_names.py` wrapper pointing at your own
   probe-results file (copy s419's — 20 lines, trivial). **At every split, test BOTH branches before
   moving on — never assume a sibling is clean by elimination.** s415, s416, and s419 have all found
   more than one bad function hiding in a single 75-name batch, and s419 additionally found the two bad
   functions do not need to share a crash site. The discipline must stay standing.
6. If a SIXTH occurrence of `last-guest-pc=0x800290d4` turns up (five known so far: `allocObjectPoolNode`,
   `tickCraftMountedAnimationEffect`, `stepObjectOrientationTowardTarget`, `updateHudHealthIndicator`,
   `buildFormatMessageGlyphBuffer`), pause ordinary relocation for one iteration and source-read what's
   at that address — see the flagged signal in s419's entry (`docs/CURRENT-TRUTH.md`). (
   `buildLevelSelectTextTextures`'s `0x8000b650` is a separate, fourth site — not part of this count.)
7. **If the actionable candidate count regenerates to 0 (item fully closed)**: this is the moment to
   close out M4 item -249 entirely — update the goal-stack/Next-steps numbering in
   `docs/CURRENT-TRUTH.md` to mark it DONE, migrate the full arc summary to
   `docs/PROJECT-OVERVIEW.md`, and re-open the USER DIRECTIVE priority stack (M3 idiom-audit-only mode
   was already exhausted per s397; M5 is closed; the next work unit after this item closes needs human
   reconfirmation on where to focus — flag this explicitly rather than picking one unilaterally).

### Environment/tooling notes (unchanged from s414-s420, still accurate)
- `RecompiledFuncs/funcs_*.c` live at
  `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c` (50 files, `funcs_0.c`
  through `funcs_49.c`). `s417_cycle.sh` deletes them automatically before every regen.
- `nm` is not on the Bash allowlist directly; prefix with `env` (`env nm <path>`).
- `find ... -delete` and glob-pattern `rm` are both blocked by the sandbox; delete generated files by
  listing exact paths to `rm` (or run one `rm -f` call per ~19-25 files to stay under the multi-op
  approval trigger) — `s417_cycle.sh` already does this internally.
- `pc-symbol` in `[CRASH]` markers is NOT a reliable cross-build crash signature — always compare
  `last-guest-pc`, not `pc-symbol` (host symbol resolution shifts as the real/stubbed function set
  changes between builds).
- Live-verify commands / `s417_cycle.sh` runs take longer than 120s (the `phase width=512` gate alone
  takes ~88-89s, plus build time) and auto-background; use `TaskOutput` with `block=true` on the
  returned task_id to wait synchronously without foreground-polling.
- The "captured N frames" line is printed by `probe.sh` to its own stdout, NOT written into the
  `run.log` inside the outdir — `s417_cycle.sh` captures it via `$(...)` command substitution, not by
  grepping the log file.
- Filtering known-bad/known-skip names from a fresh candidate list must use EXACT first-field matching,
  not substring/grep matching — a bad function's name can appear as a substring inside an unrelated
  comment line elsewhere in the symbol files (s419 hit this with `getStructField0xC`, a comment
  mentioning that name in an unrelated entry's description; harmless false-positive-in-verification but
  worth being deliberate about).
- Symbol-file edits (`main_overlay.txt`/`menu_overlay.txt`/`mission_overlay.txt`/
  `cinematic_overlay.txt`) live in the SIBLING repo `~/Documents/Tools/rogue_squadron64`, not this one.
  Per `docs/CURRENT-TRUTH.md` item -3, do NOT commit there without asking the user first — this has been
  standing, deliberate, uncommitted state since s54; the RS64Recomp build pipeline reads the working
  tree directly, so builds pick up the changes regardless of git commit state there.

## Soak queue

None currently queued — each batch's live-verify is inline (phase-gated, ~90-140s including build).
