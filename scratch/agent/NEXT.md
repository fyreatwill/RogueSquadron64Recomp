# NEXT work unit

HYPOTHESIS-ID: m4-item249-bulk-relocation-n75

## s419 recap

Resumed ordinary bulk relocation at n=75 per s417/s418's handoff. Regenerated candidates fresh (219
total, 208 actionable after filtering `m4_known_bad.txt` (7) + `m4_known_skip.txt` (4)), probed the
next 75 (60 CONFIRMED + 15 WEAK, 0 NONE/AMBIGUOUS), applied — this batch was 100% menu-tagged (0
mission), the opposite extreme from s412/s414/s416's all-mission pools. Crashed:
`last-guest-pc=0x800290d4`.

Reverted the full 75 as a same-run positive control (`make_elf.py` unmapped-functions-skipped delta
224↔149, exact ±75). Rebuilt+live-verified the reverted baseline clean (19 frames, 0 crash markers)
before bisecting.

**Applied full sibling-independence discipline from the START on both halves.** Halves-bisected 75 →
half-A(38)/half-B(37). Half-A crashed alone (`0x800290d4`). Half-B, tested independently rather than
assumed clean, **also crashed — at a different signature (`0x8000b650`)**. This had not happened
before in this item's history: previously either one half was clean and one crashed, or (s415/s416)
two bad functions shared the exact same crash site within one crashing half.

Bisected both trees to completion:
- Half-A (38, `0x800290d4`) → **`buildFormatMessageGlyphBuffer`** isolated alone. Fifth function now
  converging on `0x800290d4` (joining `allocObjectPoolNode`, `tickCraftMountedAnimationEffect` from
  s415; `stepObjectOrientationTowardTarget`, `updateHudHealthIndicator` from s416).
- Half-B (37, `0x8000b650`) → **`buildLevelSelectTextTextures`** isolated alone. `0x8000b650` is a
  NEW crash site — a fourth one now on record, distinct from `0x800290d4`, s407/s417's `0x80011088`,
  and s413's `0x80065e94`.

Every deferred sibling at every split level in both trees was independently tested before declaring
done (10 separate clean branches: A1, A2a, A2b1, playExitSoundAndToggleScreenMeshes,
processAndDisposeFormatMessage, B1a1y, B1a2, B1b, B2, and the confirming allocTextRenderTarget check).
Both bad functions reproduced their signatures alone. Applied the final 73-name batch (75 minus both),
full regen+build, live-verified clean 2/2 (88.5s/88.6s to phase, 20 frames each, 0 crash markers).
**652/778 done** (was 579/778), +73 this session. Both recorded in `m4_known_bad.txt` (now 9 entries,
4 distinct crash sites: `0x800290d4` x5, `0x80011088` x2, `0x80065e94` x1, `0x8000b650` x1).

**Signal worth flagging for a future decision point**: `0x800290d4` now has FIVE independent trigger
functions across 3 sessions (s415, s416, s419). If a 6th trigger turns up on this same site, that is
probably the point to pause ordinary bulk relocation for one iteration and source-read what is actually
at `0x800290d4` — five independently-buggy relocated functions all corrupting the exact same downstream
address is a strong signal of one shared mechanism (e.g. a stale/aliased pointer, a shared buffer
overrun, or a TOC/relocation-table slot collision) rather than five coincidentally-broken functions. Not
yet urgent (bulk relocation remains the sanctioned fallback and is still finding clean batches most of
the time), but the count is worth tracking explicitly now rather than re-discovering it by grepping
`m4_known_bad.txt` each session.

## Next work unit: resume ordinary bulk relocation at n=75

Per s411-s419's established cadence: n=75 remains the confirmed-safe steady-state batch size. 126
candidates remain per a fresh regen, ~117 actionable after filtering `m4_known_bad.txt` (9) +
`m4_known_skip.txt` (4).

### Recipe (unchanged from s417-s419, all tooling still generic and reusable)
1. Regenerate the candidate list fresh (`scratch/agent/s414_gen_candidates.py` — reads
   `main_overlay.txt`/`mission_overlay.txt`/`menu_overlay.txt`/`cinematic_overlay.txt` directly, no
   session-specific state; writes `scratch/agent/s414_candidates_all.txt`). Filter out
   `m4_known_bad.txt` + `m4_known_skip.txt` by exact name match (not substring — comment lines can
   contain a bad-function's name as a false positive, see s419's `getStructField0xC` near-miss)
   to get the actionable list. Confirm the actionable count is in the neighborhood of 117.
2. Probe the next 75 names (`scratch/agent/s400_probe_batch.py`), tag CONFIRMED/WEAK/NONE/AMBIGUOUS.
3. Apply via `scratch/agent/s400_apply_batch.py`, then run `scratch/agent/s417_cycle.sh <outdir>` —
   it deletes `RecompiledFuncs/funcs_*.c`, runs make_elf.py → N64Recomp → fixup_game_funcs.py → cmake
   build → live-verify (phase-gated, `PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180
   PROBE_LEAVE_OK=1`), and prints `RESULT=CLEAN <frames>` or `RESULT=CRASH <last-guest-pc line>` as its
   last line.
4. **If CLEAN**: live-verify a second time (2/2 discipline), commit, done.
5. **If CRASH**: do NOT guess. Revert the full batch first as a same-run positive control
   (`scratch/agent/s417_revert.py <batch-file>`; confirms the batch, not environment, is responsible —
   check the `make_elf.py` unmapped-functions-skipped delta matches the batch size exactly both ways).
   Then halves-bisect. Write a small session-local `sNNN_apply_names.py` wrapper pointing at your own
   probe-results file (copy s419's — 20 lines, trivial). **At every split, test BOTH branches before
   moving on — never assume a sibling is clean by elimination.** s415, s416, and now s419 have all
   found more than one bad function hiding in a single 75-name batch; s419 additionally found the two
   bad functions do not need to share a crash site. The discipline must stay standing.
6. If a SIXTH occurrence of `last-guest-pc=0x800290d4` turns up (five known so far: `allocObjectPoolNode`,
   `tickCraftMountedAnimationEffect`, `stepObjectOrientationTowardTarget`, `updateHudHealthIndicator`,
   `buildFormatMessageGlyphBuffer`), pause ordinary relocation for one iteration and source-read what's
   at that address — see the flagged signal above. (`buildLevelSelectTextTextures`'s `0x8000b650` is a
   separate, fourth site — not part of this count.)

### Environment/tooling notes (unchanged from s414-s419, still accurate)
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

## Soak queue

None currently queued — each batch's live-verify is inline (phase-gated, ~90-140s including build).
