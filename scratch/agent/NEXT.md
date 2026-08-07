# NEXT work unit

HYPOTHESIS-ID: item-301-scan-buckets

## s467 CLOSED item -300 outright (`NODE_LIST_HEAD_GUARD`/`NODE_LIST_HEAD_WRITE_GUARD`, global
`0x8011A4B8`, 20 read-guard + 10 write-guard sites) AND folded item -299's 2nd confirm soak

Full derivation, fix, build/live-verify results, and confirm-soak recipe:
`docs/CURRENT-TRUTH.md` item -300, `PORTING-STATE.md` Session 467. Notable: this bucket turned out
to be TWO distinct downstream shapes (a `FREELIST_NEXT_GUARD`-style conditional write needing only
a read guard, and a `DL_LIST_RESET_GUARD`-style write-through-reload needing its own separate write
guard) rather than the single reusable shape s466's writeup hoped for — caught by reading full
per-site context up front instead of assuming uniformity from a short sample. Live-verify: **0
`[CRASH]` across the ENTIRE 300s schedule** (all 10 key presses fired) — notably cleaner than most
recent sessions' live-verify runs, which usually hit an unrelated background-noise crash partway
through. 0 fires on both new guards (matches item -287's baseline), 0 regression on any sibling
guard, `hangarbay-entry` n=33 (positive control). Confirmation soak queued:
`scratch/agent/soak_queue/s467_nodelisthead_confirm.sh` (not yet run by the loop as of this write —
check `scratch/agent/SOAK-RESULTS.md` tail next session and fold its verdict into the ledger before
starting new work).

Also folded this session: `s466_dlbufferpool_confirm`'s full `run.log` (not just the probe.sh
one-line summary) — a 2nd independent confirmation of item -299's true-negative result (0 fires on
all 4 sibling guards tested, crashed on the same already-catalogued `coalesceFreeHeapBlocks+4424`
family, unrelated). No ledger change needed there, already correctly CLOSED.

## This session's top work unit: classify the next candidate bucket from s465's scan

With items -299 and -300 both closed, s465's scan (`scratch_s465_scan.py`, N64Recomp repo,
untracked — re-run it fresh or re-read its saved output if still on disk) has NO more buckets in
the tightly-concentrated `funcs_3.c`/`funcs_4.c`-only category that produced both of the last two
closes. The remaining buckets are all more scattered (multiple files, including `funcs_6.c`-only
populations this lineage hasn't touched before) — ranked by raw site count:

1. **`hi16=0x8013, offset=0x7CE4`** (45 sites, 9 files) — largest remaining bucket, but spread
   across 9 files instead of the usual 2, so expect MORE shape diversity than items -299/-300, not
   less. Budget for reading a large, spread sample (10+ sites across multiple files) before
   assuming any single shape, per this session's own lesson.
2. `hi16=0x8013, offset=-0x70F8` (31 sites, `funcs_6.c` ONLY) — a new file this lineage hasn't
   examined before; worth checking whether `funcs_6.c`'s code (audio/sequencer adjacent, per
   `SONGTEMPO_TABLE_GUARD`'s own `funcs_25.c` neighbor and `funcs_6.c`'s 3 already-excluded
   `COMPARE_ONLY` sites from item -299's own scan) has a different idiom shape than the display-list
   code funcs_3.c/funcs_4.c have shown so far.
3. `hi16=0x8012, offset=-0x5BBC` (30, 4 files)
4. `hi16=0x8013, offset=-0x7104` (29, `funcs_6.c` only)
5. `hi16=0x8011, offset=-0x35E0` (23, 9 files)
6. `hi16=0x8013, offset=0xB50` (21, 11 files)

### Step 1: classify the top-ranked bucket's downstream use, READING FULL CONTEXT PER SITE

Write `scratch_s468_classify_<offset>.py` (check the actual session number at start of work)
modeled on `scratch_s467_classify_5b48.py` (N64Recomp repo, untracked). **This session's own
discriminating lesson**: do NOT stop at a short (~14-line) sample window and assume the shape
extends past it — item -300 needed 30+ lines of context to reveal a SECOND, structurally different
write pattern hiding past an already-existing unrelated guard block. If the classify script's
window doesn't reach a function's `return`/`jr $ra`, widen it until it does, for at least the first
several sites of each file represented in the bucket.

### Step 2: if a real deref/write-through-reload risk emerges, model the guard(s) directly on the
now-3-deep precedent set

- Read-only risk gating a conditional write (`if (rD != 0) { write; goto L; } goto skip; <dup>;
  skip:`): `FREELIST_NEXT_GUARD` (s441) / item -300's read-guard half — force the deref result to
  whichever value (0 or nonzero) makes the gating `if` skip the write.
- Reload register used DIRECTLY as an unconditional write address later in the same function:
  `DL_LIST_RESET_GUARD` (item -298) / item -300's write-guard half — skip the write entirely on an
  invalid head (0 is not a safe write ADDRESS, unlike a safe READ substitute).
- If a genuinely new third shape appears, don't force it into one of the above — write a new
  targeted patch and document the new shape's structure explicitly in the same style as this
  session's writeup.

### Step 3: patch, regen, build, live-verify, queue confirm soak — standard recipe

1. `cd ~/Documents/Tools/N64Recomp && python3 -c "import glob,os; [os.remove(f) for f in
   glob.glob('RecompiledFuncs/funcs_*.c')]"` (Python `os.remove` over `glob`, NOT bare `rm -f`).
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. `python3 fixup_game_funcs.py` — audit the report for the expected site count(s) AND confirm
   sibling guard counts are UNCHANGED: `DL_LIST_APPEND_GUARD` 84, `DL_LIST_RESET_GUARD` 84,
   `SIBLING_PTR_WRITE_GUARD` 119, `DL_BUFFER_POOL_GUARD` 84, `NODE_LIST_HEAD_GUARD` 20,
   `NODE_LIST_HEAD_WRITE_GUARD` 10 — a regression in any of these means the new regex accidentally
   clobbered an existing guard's anchor text.
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from the
   RogueSquadron64Recomp repo root (or `cd build && cmake --build . -j8`).
6. `strings build/RogueSquadron64Recomp | grep -c <new-tag>` — confirm it matches the site count.
7. Live-verify from `build/`: arm ALL passive guard/breadcrumb env vars (copy the full list from
   `scratch/agent/soak_queue/s467_nodelisthead_confirm.sh`) plus the new guard's own
   `ROGUESQ_LOG_<NEW_TAG>=1`, `PROBE_KEYS_FROM_PHASE=1`, full schedule, SIGKILL at teardown.
   Discriminating outcome: 0 new-guard fires expected (matches item -287's true-negative baseline)
   PROVIDED `hangarbay-entry` (or equivalent) shows the code was actually reached (positive
   control, iron rule 1).
8. Write `scratch/agent/soak_queue/s468_<name>_confirm.sh` (self-contained, same shape as
   `s467_nodelisthead_confirm.sh`) for the loop to run.

## Fallback if the top bucket turns out unreasonably scattered/diverse for one session

Move to the next bucket in the ranked list above. If NONE of the remaining 6 buckets close cleanly
within budget (iron rule 8: 3 consecutive iterations on this slug without a close forces a pivot
preamble), consider whether the scan's `count >= 20` threshold is now surfacing genuinely
lower-value, more scattered idioms than the tightly-concentrated `funcs_3.c`/`funcs_4.c` core that
produced every real finding so far — that would be a legitimate signal to close this scan-driven
sub-arc and look for a different M3 discovery method, same as s397 did once before.

## Soak queue status

`scratch/agent/soak_queue/s467_nodelisthead_confirm.sh` is queued as of this session end (not yet
run by the loop) — check `scratch/agent/SOAK-RESULTS.md` tail at the start of next session and fold
its verdict into the ledger before starting new work, per the standing soak-queue consume step.

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

Unchanged from prior sessions — 10 of item -296's 119 sites sit in `submitSceneNodeRender`, tied to
a still-open 2-occurrence wait-for-recurrence breadcrumb. 0 fires across every soak so far including
s467's (this session's own live-verify run also showed 0 for this guard). Passive, no action needed
unless a soak result shows a fire.
