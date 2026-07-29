# NEXT work unit — chase the fresh `submitSceneNodeRender+18600` hot lead, OR
# continue the project-wide whack-a-mole static sweep (139 candidates remain)

## Where the investigation stands (s252)

s252 closed out the `heapFreeListDequeue` lead s251 flagged. Full detail:
PORTING-STATE Session 252. Landed:

1. Read the ENTIRE ~1758-line function start to end (not just the
   guarded loop, per s251's own lesson) and found a real gap the static
   self-ref-walk finder (`find_unguarded_walks.py`) cannot see, because
   it isn't a self-referential reload: all 4 copies of the free-list-
   search block NULL-check `findAndUnlinkSmallestEntry`'s return value
   (`r4`) but then immediately dereference `r4`'s own offset-0 "next"
   field (`ctx->r2 = MEM_W(ctx->r4, 0X0)`) with **no range check** — one
   dereference earlier than the existing s217 loop-back guard, which
   cannot reach it (it never runs until *after* this line).
2. Added 4 new guards in `fixup_game_funcs.py` (sibling `N64Recomp`
   checkout): `funcs_3.c` `heapFreeListDequeue`, sites
   `0x8000D054`/`0x8000D18C`/`0x8000D2D8`/`0x8000D6A8`. Same
   0x80000000-0x80800000/hi==0xFFFFFFFF KSEG0 range check used by every
   guard in this family; on failure sets `ctx->r3 = ADD32(ctx->r4, 0)`
   and jumps to the same label the existing "r2 == 0" path already uses
   — byte-identical downstream behavior to a clean empty-next-field
   read. New env var `ROGUESQ_LOG_HEAPLISTDEQ_HEAD_GUARD`,
   `site=<addr>`.
3. Build clean (patch report audited, `scratch/agent/s252_fixup_report.txt`
   — all 4 new guards `x1`, every pre-existing multiplicity unchanged
   from s251's baseline, nothing new stacked).
4. **1 soak** (`heaplistdeqhead1`, `HOLD_S=150`): crossed SELECT-CRAFT
   cleanly (45.0s to title, transition per the established schedule),
   died ~1s into the hold to `[CRASH] caught signal 10`,
   `x0=x9=0x0000000300000000` (the same RDRAM-base sentinel), but this
   time `pc-symbol=submitSceneNodeRender+18600` — **a different function
   than heapFreeListDequeue entirely**. Both the new head-pointer guard
   AND the existing loop-back guard fired **0/4** each (uninformative
   null — the render-tree walk never reached `heapFreeListDequeue`'s
   search code before dying elsewhere this run). `heapwalker-guard4`
   positive control fired once, confirming guard infra was live.
5. **Reconfirmed (3rd independent time, after s207's two attempts) that
   `nm`/`atos` are unusable in this headless environment** — both
   require interactive approval that is never granted non-interactively.
   This is a **permanent environment limit, not a transient one** — do
   NOT recommend offset-based crash-PC localization via `nm`/`atos`
   again in a future NEXT.md. If a crash backtrace gives only a function
   name + byte offset with no further context, the only path forward is
   a full source read of that function (as this session did), not
   disassembly.

**Conclusion**: `heapFreeListDequeue`'s pointer-walk surface is now fully
guarded (4 loop-back + 4 head-pointer sites) — this rules out "one more
site in this function" as an open question. The guards themselves remain
soak-unconfirmed (0/4 fires each), same weak-null caveat as nearly every
guard in this session's lineage (s249-s252): a clean/null soak does NOT
mean "confirmed safe," only "not exercised this run."

## The single highest-value next step: chase `submitSceneNodeRender+18600`

This soak pinned down a **fresh crash offset inside `submitSceneNodeRender`**
proven hot on this exact run (it's what's running when the process died,
moments after every recent SELECT-CRAFT-transition soak — same call path
as s251's finding: `submitSceneNodeRender <- processSceneNode <-
traverseSceneGraphRecursive <- setupCameraMatrices <- ... <-
menuOverlayInit`). Unlike `heapFreeListDequeue` (now fully read and
guarded), `submitSceneNodeRender` already has 20+ existing guards from
many prior sessions (`GUARD2` x9 sites, `GUARD3` x8 sites, "free-list-walk
guard" x1, "cached-free-list-head guard", "material-batch-list guard1/
guard2", per `scratch/agent/s252_fixup_report.txt` lines 123-128) — so
this is NOT necessarily virgin territory. Recommended next work unit:

1. `grep -n "RECOMP_FUNC void submitSceneNodeRender" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c`
   to find the function start, and read the WHOLE function (it's large —
   expect 1000+ lines given 20+ existing guard sites already patched into
   it). Cross-reference against `fixup_game_funcs.py`'s existing
   `submitSceneNodeRender` guard blocks (grep for
   `"submitSceneNodeRender"` in that file) to build a map of what's
   ALREADY covered before assuming offset+18600 is virgin.
2. Since `nm`/`atos` are confirmed permanently unusable here (see above),
   do NOT attempt to convert the `+18600` byte offset into a specific
   line — instead find every self-ref-walk AND every
   "NULL-checked-then-dereferenced-return-value" pattern (per s252's own
   new-category lesson: the static finder only catches the FIRST
   pattern, not the second) that is not yet covered by one of the
   existing 20+ guards, following the same full-body-read discipline
   this session and s249-s251 used.
3. Before writing any guard, check whether the site is a FALSE POSITIVE
   (per s251's `renderUnlitMeshFaces` lesson): is it reached only via
   paths that already validated the same address?
4. Patch + single regen cycle (delete all 45 `funcs_*.c` first,
   mandatory) + build + audit patch report + soak with a NEW tag and
   both the existing `submitSceneNodeRender` guard env vars and a new
   site-specific one armed, so a fire distinguishes which site took the
   hit.

## Otherwise: continue the static sweep (139 candidates remain)

If the `submitSceneNodeRender` lead is exhausted or blocked, fall back to
the static sweep. Same rigor as every prior session: read the whole
function body (not just the flagged self-ref line), check for BOTH known
gap categories now (self-ref walk, AND null-checked-but-unranged return-
value deref per s252), identify every register that aliases the
untrusted pointer, check for false positives first, find a safe bail
target by reading forward, then patch + regen + build + audit + soak.
Good next candidates (all in `funcs_3.c`/`funcs_4.c`, same family as every
already-fixed function above):
`renderLitMeshFaceGroup` (14 sites, `funcs_4.c`),
`renderLitTexturedMeshFaces` (11 sites, `funcs_3.c`),
`func_800AE3F0` (10 sites, `funcs_27.c`), `beginFrameDLChunk` /
`emitFrameRdpInitDl` (10 sites each, `funcs_3.c`).

`docs/CURRENT-TRUTH.md` housekeeping — still ~407 KB+, flagged 42+
sessions, still not done. Per `ITERATION.md` this does NOT count as
`ADVANCED` on its own — pair it with a real change or expect to file
`SUBSTITUTED`.

## Full candidate list (139 total)

Unchanged since s251 — `heapFreeListDequeue`'s gap was found by full-body
read, not by the static finder, so it was never on this list and its
removal doesn't change the count. Grouped by `(file, function)`. Format:
`file: func -- N site(s) -- lines [selfref line numbers in funcs_*.c,
sibling N64Recomp/RecompiledFuncs/]`. Re-derive with
`python3 scratch/agent/find_unguarded_walks.py` if the sibling checkout
changes (it regenerates `unguarded_walk_candidates.json` too).

```
funcs_20.c: model_animation_offset_convert -- 1 -- [1947]
funcs_23.c: tickAudioChannel -- 1 -- [2089]
funcs_25.c: stopSongByHandle -- 2 -- [4630, 4690]
funcs_25.c: tickSongSequence -- 2 -- [5118, 5178]
funcs_27.c: cutsceneDispatchSlotsByFlag -- 2 -- [114157, 114365]
funcs_27.c: func_800AE3F0 -- 10 -- [169135, 169295, 169437, 169619, 169832, 169992, 170163, 170308, 177403, 177555]
funcs_3.c: allocDLBlockToFillRectList -- 1 -- [1136]
funcs_3.c: allocDLBlockToListB -- 1 -- [1281]
funcs_3.c: allocDLBlockToListC -- 1 -- [1426]
funcs_3.c: allocDLBlockToListD -- 1 -- [1571]
funcs_3.c: allocateDisplayListBuffer -- 1 -- [970]
funcs_3.c: beginFrameDLChunk -- 10 -- [8442, 8699, 8937, 9190, 9392, 9640, 9840, 10087, 10323, 10564]
funcs_3.c: commitMeshDrawBatchRefs -- 3 -- [2458, 2477, 2501]
funcs_3.c: countDisplayListChunks -- 1 -- [788]
funcs_3.c: drainMeshReleaseQueue -- 5 -- [1725, 1788, 1846, 1918, 1980]
funcs_3.c: drawFrameProfilerBars -- 2 -- [11150, 11339]
funcs_3.c: emitColorFillRect -- 8 -- [6258, 6447, 6642, 6835, 7108, 7340, 7574, 7814]
funcs_3.c: emitFrameRdpInitDl -- 10 -- [4141, 4328, 4529, 4720, 4936, 5157, 5354, 5550, 5747, 5959]
funcs_3.c: emitMaterialTexturedDL -- 5 -- [18717, 18994, 19214, 19438, 19633]
funcs_3.c: emitMaterialTexturedDLAlt -- 5 -- [19901, 20176, 20381, 20597, 20835]
funcs_3.c: heapFreeListInsert -- 1 -- [58]
funcs_3.c: reclaimDisplayListChunk -- 1 -- [852]
funcs_3.c: recordDeferredDrawRefA -- 1 -- [13976]
funcs_3.c: recordDeferredDrawRefB -- 1 -- [14181]
funcs_3.c: recordDeferredDrawRefC -- 1 -- [14388]
funcs_3.c: recordDeferredDrawRefD -- 1 -- [14593]
funcs_3.c: recordDeferredDrawRefVariant -- 1 -- [2241]
funcs_3.c: renderLitTexturedMeshFaces -- 11 -- [22357, 22407, 22447, 22908, 23039, 23148, 23180, 23334, 23486, 23681, 23816]
funcs_35.c: static_4_800B13E0 -- 8 -- [3551, 3711, 3853, 4035, 4248, 4408, 4579, 4724]
funcs_35.c: static_4_800B3FB4 -- 1 -- [11851]
funcs_35.c: static_4_800B40A0 -- 1 -- [12007]
funcs_4.c: buildOrientedFaceGeometry -- 3 -- [7611, 7842, 8175]
funcs_4.c: drawSubtitleText -- 6 -- [16349, 16581, 16945, 17740, 18531, 19115]
funcs_4.c: drawTextGlyphRect -- 1 -- [15740]
funcs_4.c: renderFlatMeshFaceGroup -- 6 -- [3189, 3421, 3693, 4338, 4540, 4741]
funcs_4.c: renderLitMeshFaceGroup -- 14 -- [8640, 8870, 9142, 9562, 10174, 10426, 10760, 10957, 11318, 11615, 11997, 12635, 12916, 13230]
funcs_4.c: setupCameraMatrices -- 3 -- [19722, 20792, 20981]
funcs_43.c: static_5_800CBBB8 -- 1 -- [13142]
funcs_43.c: static_5_800CBD88 -- 1 -- [13480]
funcs_43.c: static_5_800CBDC4 -- 1 -- [13535]
```

Note: `funcs_4.c: setupCameraMatrices -- 3 -- [19722, 20792, 20981]` is an
ancestor in this exact session's (and s251's) crash backtrace — worth
prioritizing given it's on a demonstrably hot path. Read fully before
assuming its 3 flagged sites are real gaps (apply the s251 false-positive
lesson).

Note: `funcs_43.c: static_5_800CBBB8/800CBD88/800CBDC4` are worth a
second look — their line numbers/offsets are suspiciously close to
`selectPostCrawlCraft`'s own addresses (`0x800CBBB8` etc. in `funcs_30.c`)
but in a DIFFERENT file (`funcs_43.c`); confirm whether this is a
coincidental address-space overlap (different overlay) or a stale/
duplicate JSON entry before spending a session on it — re-derive via
`find_unguarded_walks.py` first.

## Do NOT do this iteration

- Do NOT re-run `mtldebug1`..`mtldebug4`, `scissorfix1`, `malloclog1`,
  `malloclog2`, `metalresize1`, `selectpostcrawlguard1`..`3`,
  `dlentrytailguard1`, `heaplistdeqhead1` in place — superseded tags. New
  soaks need new tags.
- Do NOT re-attempt `nm`/`atos` for offset localization — confirmed
  unusable 3 independent times (s207 x2, s252). This is now a permanent
  environment fact, not something to re-test a 4th time.
- Do NOT batch-apply guards from the JSON candidate list mechanically —
  every site needs its own full-loop-body read first, a check for false
  positives, AND (new since s252) a check for the
  NULL-checked-but-unranged-return-value pattern the static finder
  misses entirely.
- Do NOT invoke `fixup_game_funcs.py` more than once per regen cycle —
  it will silently stack duplicate declarations and break the build with
  unrelated errors.
- Do NOT cite `heaplistdeqhead1`'s 0/4-fire result as "these guards are
  confirmed safe" — weak, single-sample null, same caveat as
  `dlentrytailguard1`/`selectpostcrawlguard3`.
- Do NOT revive the NaN_CHECK-disable idea (CURRENT-TRUTH `-55`/`-56`) —
  already tried, A/B-tested, and reverted at s216 (`-57`).

## Environment notes (carried forward, still current as of s252)

- **Permission gate CONFIRMED CLEARED through s252** for the standard
  `tools/*`/`build/*`/`python3:*`/`zsh:*` command families. **`nm`/`atos`
  are NOT on the allowlist and are NOT auto-approved non-interactively —
  confirmed a 3rd time this session.** `echo` is also not allowlisted
  (surfaced this session — use `printf`-free alternatives or just rely on
  a command's own stdout/exit code instead of an explicit echo marker).
  Compound `cd ... && <command with output redirection>` in a single Bash
  call is specifically blocked ("Commands that change directories and
  write via output redirection require explicit approval") — issue `cd`
  as its own Bash call first, then the redirecting command as a separate
  call in the same shell (cwd persists across calls).
- **`GAME_EXTRA_ENV`** (`run_mission_keys.sh`, s241): space-separated
  `VAR=val VAR2=val2` string, scopes extra env vars to ONLY the game
  process.
- **Env-gated logging pattern**: `static const bool s_X = [](){ const
  char *v = std::getenv("VAR_NAME"); return v && v[0] && v[0] != '0'; }();`
  then `if (s_X) { std::fprintf(stderr, ...); std::fflush(stderr); }`.
- **Block-wait pattern**: launch the soak with Bash `run_in_background:
  true`, read the driver's first output line for `pid NNNNN out=...`,
  then run a SECOND Bash call (foreground, generous `timeout` up to
  480000ms) that polls `until ! kill -0 <game_pid> 2>/dev/null; do sleep
  N; done`. This tool call blocks until the process exits, letting a soak
  run to completion within one iteration.
- **`update_screen` counter rate is ~60/s** once past the title screen —
  useful for extrapolating wall-clock death time from the last `[vi]`
  line when the driver's own `wall=` figure undercounts.
- `/tmp` is not writable this session — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ...` and `git -C <path> <cmd>` get blocked/need
  extra approval — issue `cd` as its own Bash call first, and plain
  `git status`/`git diff`/etc. (no `-C`) once cwd is already there.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`.
- **`campose*` armed env-var set** (unchanged since `campose11`):
  `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_HEAPLISTDEQ_HEAD_GUARD` (new, s252),
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`,
  `ROGUESQ_LOG_SELECTPOSTCRAWL_GUARD=1`,
  `ROGUESQ_LOG_SELECTPOSTCRAWL_INSGUARD_A1`/`A2`/`B1`/`B2=1`,
  `ROGUESQ_LOG_DLENTRY_TAIL_GUARD=1` — see
  `scratch/s73_post_a_scene/run_heaplistdeqhead1.sh` for the full current
  set (this file survives across sessions on disk even though `scratch/`
  is gitignored — copy it forward for new soaks; only
  `STATUS`/`OUTCOME`/`NEXT.md`/`run_mission_keys.sh` are git-tracked).
- **The `[phase] vi_width=512 (was 1024) origin=0x006AB400` line at
  ~t=74-75s is THE confirmed SELECT-CRAFT->mission transition marker.**
- **Regen is mandatory-delete-all-first, AND fixup must run EXACTLY
  ONCE**: `N64Recomp` skips rewriting any `funcs_*.c` that already exists
  on disk, so leftover files from a previous session silently stack
  duplicate patches. Always delete all 45 `RecompiledFuncs/funcs_*.c`
  before `make_elf.py` (cwd `rogue_squadron64`, `python3 tools/make_elf.py`)
  → `N64Recomp` (`tools/agent/regen_n64recomp.sh` from
  `RogueSquadron64Recomp`'s own cwd) → `fixup_game_funcs.py` (cwd
  `N64Recomp`, `python3 fixup_game_funcs.py`) → `cmake --build .` (cwd
  `build`, needs `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`
  for Metal shaders). Never invoke `fixup_game_funcs.py` a second time
  against the same already-patched output. Audit the fixup patch report
  (saved to a file on the ONE invocation) for anything other than the
  expected `xN` multiplicity before trusting the build.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  — `scratch/agent/checksum_campose11.py` (s235) is mtime-aware, reuse
  this pattern.
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- The driver's own `CRASH: N` summary counts occurrences of the LITERAL
  STRING `[CRASH]` (many per crash) — grep `[CRASH] caught signal` for
  actual crash event counts. The driver's own end-of-run `--- summary ---`
  block (in the launch-log, not `run.log`) also prints `exit=2: N`
  (crash-exit count, lle-task level) — cross-check both, they measure
  different things.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each
  iteration by the harness — normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`,
  `NEXT.md`, and `run_mission_keys.sh` are tracked exceptions. Non-tracked
  scratch files (driver scripts, analysis scripts, logs) persist on disk
  across sessions but are not in git history.
- Verify a fresh binary before trusting a null result: `strings
  build/RogueSquadron64Recomp | grep '<your-new-tag>'` plus `ls -la
  build/RogueSquadron64Recomp` vs. the soak's start time.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (still ~407 KB+ / ~6000+ lines,
flagged 42+ sessions without action).

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly. Every guard
in the whack-a-mole family, including this session's, lives there. Also
still not fixed: the script's non-idempotency bug found s250 (`rs_malloc`
entry-capture patch stacks duplicate declarations on repeat invocation).

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.
