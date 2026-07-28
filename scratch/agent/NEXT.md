# NEXT work unit — either the 3rd (and last, per rule 8) blind sceneptrguard
# soak, OR (likely higher value) a defensive guard on queueGPUUploadTMEM,
# the project's most-recurring crash and 2/2 blocker of the last two soaks

Read PORTING-STATE Session 191 in full before doing anything else (`grep -n
"^## Session 191" PORTING-STATE.md`); this file only has the actionable
summary. Also read docs/CURRENT-TRUTH.md's `-40` next-steps item (top of the
list).

## Why this is the next work unit (read before doing anything else)

s190 landed a fix (`processSceneNode` node-pointer guard,
`ROGUESQ_LOG_SCENE_NODE_PTR_GUARD`) whose effectiveness is still untested —
two soaks since (`sceneptrguard3` in s190, `sceneptrguard4` in s191, byte-
identical config) have both died BEFORE the 9660-9800 decisionN window the
fix targets, at decisionN 8053 and 7897 respectively. Critically, **each
soak died to a DIFFERENT already-catalogued, unrelated crash** —
`reserveAndEmitDLEntry` (game-thread SIGBUS) in s190,
`queueGPUUploadTMEM` (RT64 graphics-thread SIGABRT assert,
`lib/rt64/src/render/rt64_texture_cache.cpp:1285`) in s191. This refutes
`reserveAndEmitDLEntry` as a specific recurring blocker (was 1/2, not 2/2)
and confirms the "ordinary soak-to-soak crash variance" framing — but
sharpens it: it's not variance among processSceneNode-adjacent bugs, it's
variance among the project's whole ~15-18-strong catalogue of still-open
crash classes, and `queueGPUUploadTMEM` is the single most frequent one in
the project's entire history (first seen s86, 8+ occurrences, open goal-
stack item M3) — it just killed 2/2 fix-soaks in a row before they got far
enough to test anything.

`[scene-node-ptr-guard]` has fired **0 times across both soaks** — the
fix's target mechanism (corrupted sibling pointer reaching
`processSceneNode`) has never been directly observed since the fix landed.
The underlying question (does the fix work, does decisionN push past 9792,
does the `-35` stall signature appear) remains completely untested — not
refuted, just never reached.

## Two valid options, in order — pick ONE per iron rule 8 (do not do both
## in the same iteration; that's two work units)

### Option A — one more blind soak (last one allowed before mandatory pivot)

This is strike 2 of 3 on "does a fix-soak reach the target window" (iron
rule 8: 3 consecutive same-hypothesis iterations with no discriminating
result → stop and pivot). One more identical attempt is still in budget.
If you pick this and it ALSO dies early to an unrelated already-catalogued
bug, that's the 3rd strike — do not run a 4th; write up the pattern and
pivot to Option B (or something else) in the SAME iteration's writeup, per
rule 8's own instruction ("pick the highest-information-value next probe").

1. Copy `scratch/agent/run_sceneptrguard4.sh` to `run_sceneptrguard5.sh`
   (tag-only change, keep the env block byte-identical).
2. Run it exactly like the prior 2 attempts (background + `TaskOutput`
   block, or foreground with a generous timeout ~480s+).
3. Check: does decisionN reach past 9792? Does `[scene-node-ptr-guard]`
   fire at all (positive control)? If it crashes early again, which
   already-catalogued class this time (grep the backtrace against
   PORTING-STATE)?

### Option B — guard `queueGPUUploadTMEM` (likely higher information value)

Attacks the crash that has now blocked 2/2 fix-soaks and is the single most
historically-recurring bug in the whole project. Source (already read this
session, `lib/rt64/src/render/rt64_texture_cache.cpp:1284-1303`):

```cpp
void TextureCache::queueGPUUploadTMEM(uint64_t hash, uint64_t creationFrame, const uint8_t *bytes, int bytesCount, int width, int height, uint32_t tlut, const LoadTile &loadTile, bool decodeTMEM) {
    assert(!decodeTMEM || ((width > 0) && (height > 0)));

    TextureUpload newUpload;
    ...
```

No locks are held and no resources are acquired before the assert — a bare
early `return;` right after a logged bail is a clean, safe skip-the-upload
site. Mirror the project's established defensive-guard pattern (`rs_malloc`
s173, `rs_free` s187, `scene-node-ptr` s190): new `ROGUESQ_LOG_*` env var
(suggest `ROGUESQ_LOG_TMEM_ZERO_GUARD`, distinct from the pre-existing
unused `ROGUESQ_LOG_TMEM_ZERO` diagnostic-only var mentioned in older
sessions — check it's not already claimed with `grep -rn
ROGUESQ_LOG_TMEM_ZERO lib/`), log guest-visible context (hash, width,
height, decodeTMEM) once per fire with a bounded counter, then `return;`
instead of falling through to the assert.

Steps:
1. `grep -n "ROGUESQ_LOG_TMEM_ZERO" lib/rt64/src/render/rt64_texture_cache.cpp
   lib/rt64/src -r` first — confirm no existing guard already covers this
   exact site (older sessions added `ROGUESQ_LOG_TMEM_ZERO` as a diagnostic
   logger elsewhere in the upload path, NOT a guard on this assert — verify
   that's still true before assuming a green field).
2. Add the guard in `lib/rt64/src/render/rt64_texture_cache.cpp` near line
   1285 (getenv-gated, matches the pattern of other `lib/` guards already in
   this file/tree if any exist — grep for an existing `getenv(` pattern in
   `lib/rt64` first to match style; if none exists there yet, mirror the
   `N64Recomp/fixup_game_funcs.py` guards' getenv-once-cached idiom).
3. This is a PURE `lib/rt64` runtime change — no regen/fixup pipeline
   needed. Just `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
   cmake --build build --target RogueSquadron64Recomp -j`.
4. **`./submodule-patches/export.sh` (relative path from repo root) +
   `git add`/`git commit` in THIS SAME session** — `lib/` edits not
   exported and committed this session are lost at the next reset (hard
   rule, CLAUDE.md).
5. Soak with the guard active (same s188/s190/s191 env block plus the new
   var) — positive control is the guard firing at least once; if it fires,
   check whether the run then survives further (reaches a new decisionN
   high-water mark, or reaches the 9660-9800 window and tests the ACTUAL
   processSceneNode question this whole lineage has been trying to reach).

## Do not

- Do not do BOTH options in one iteration — pick one, per the single-work-
  unit rule.
- Do not re-touch the `processSceneNode` node-pointer guard itself — still
  fixed and verified intact (confirmed again by source grep in s191).
- Do not treat `reserveAndEmitDLEntry` as a recurring blocker needing its
  own fix — s191 refuted that (1/2 occurrences, not 2/2).
- Do not attempt to root-cause `queueGPUUploadTMEM`'s actual corrupted-
  width/height source (goal-stack M3, "root-cause/fix") — Option B above is
  a defensive skip-guard only, matching the project's established pattern
  for unblocking soak progress, not a real fix. Root-causing it is a much
  larger, separate investigation out of scope here.
- Do not re-attempt root-causing the underlying `rs_free` free-list
  corruption source itself (s85-s114 chase) — still out of scope.
- Do not turn on `ROGUESQ_LOG_THREAD_RESUME=1` (s93's confound).

## Blocking on a long-running soak (learned the hard way, still current)

Run the driver script as a single foreground Bash call with output
redirected to a log file and a generous timeout (~480s), OR launch with
`run_in_background: true` and block on the returned task ID via
`TaskOutput(task_id, block=true, timeout=300000-480000)` — this is the
correct way to synchronously wait for a soak before writing the exit-
contract docs; ending the turn while a background soak is still running
trips the Stop hook's exit-contract check prematurely.

## This session's environment notes (carry forward, still current)

- **`N64Recomp/fixup_game_funcs.py` is non-idempotent** — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. If adding a NEW patch: regenerate fresh first (`zsh
  tools/agent/regen_n64recomp.sh`), THEN run `python3
  /absolute/path/to/N64Recomp/fixup_game_funcs.py > log` exactly once. Grep
  the log for the new patch's report line to confirm exactly x1, and check
  older patches' lines are ALSO x1 (not x2). **Not relevant to Option B** —
  that's a pure `lib/rt64` change, no fixup pipeline involved.
- A pure `lib/N64ModernRuntime`/`lib/rt64` runtime change (not a
  `RecompiledFuncs/*.c` patch) does NOT need the regen/fixup pipeline at
  all — just `cmake --build build --target RogueSquadron64Recomp -j`
  directly.
- Re-running the same soak script/tag **overwrites** the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied — use
  absolute paths, no `cd`, one command per Bash call (including a trailing
  `echo` after a redirected command). `echo foo; echo bar` and `cmd;
  echo $?` also get flagged ("Contains simple_expansion") — one command,
  one effect, per Bash call.
- `git -C <path> ...` AND `cd <path> && git ...` (combined in one Bash call)
  both trigger approval prompts that a non-interactive session can't clear —
  if you need git state from a directory other than the repo root, either
  accept that a plain `git <cmd>` after a SEPARATE `cd` Bash call may still
  need approval, or just use direct file reads/greps instead of git.
- `submodule-patches/export.sh` must be invoked as
  `./submodule-patches/export.sh` (relative) from the repo root — absolute
  path gets denied.
- A large `run.log` (millions of lines) is fine to `grep -c`/`grep -n >
  outfile` directly — just don't `cat`/`Read` it wholesale.
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py`, or the `[CRASH]` stack dump.
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- Output redirection is sandboxed to the session's allowed working
  directories (this repo, N64Recomp, rogue_squadron64) — redirecting to
  `/tmp/...` gets blocked; use a path under `scratch/agent/` instead.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now over ~36 KB (growing every session) —
migrate durable mechanism/architecture material to PROJECT-OVERVIEW.md and
prune superseded detail, paired with a real experiment. Flagged for many
sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session. Still flagged
for the user, not committed autonomously.
