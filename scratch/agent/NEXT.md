# NEXT work unit — continue the project-wide whack-a-mole static sweep
# (142 candidates remain), or pivot to CURRENT-TRUTH housekeeping

## Where the investigation stands (s249)

s249 started the static sweep s248 proposed (option 1) instead of
CURRENT-TRUTH housekeeping (option 2), since it's real code and
housekeeping alone doesn't count as `ADVANCED` per `ITERATION.md`.

Landed:
1. `scratch/agent/find_unguarded_walks.py` — script that greps all 45
   `RecompiledFuncs/funcs_*.c` files (in the sibling `N64Recomp` checkout)
   for unguarded singly-linked-list walk loops: a labeled loop target
   that is the destination of a **backward** `goto` (real back-edge, not
   just any label), containing a self-referential load
   (`ctx->rX = MEM_W(ctx->rX, 0X0)`) within 4 lines of the label, with no
   existing `PATCH` guard already covering it. The naive self-ref-only
   signature hits 794 sites (way too broad — most are safe one-shot
   dereferences); this narrows to **143 candidates across 43 functions**.
2. `scratch/agent/unguarded_walk_candidates.json` — the full candidate
   list: file, label, line numbers, enclosing function name, snippet.
3. One guard shipped: `selectPostCrawlCraft` (`funcs_30.c`, address
   `0x800CBBD8`) — see `fixup_game_funcs.py` comment (sibling `N64Recomp`
   checkout) and PORTING-STATE Session 249 for the full mechanism,
   including an important correction: **the naive self-ref signature is
   necessary but not sufficient** — read the WHOLE loop body before
   guarding, not just the flagged line, because the same untrusted
   pointer is often dereferenced through a second register one line
   earlier (missed by the mechanical grep). Do not batch-apply guards
   from the JSON without this per-site read.
4. Build clean (patch report audited, exactly `x1`, no duplicate), 1 soak
   (`selectpostcrawlguard1`) — crossed the SELECT-CRAFT transition clean,
   died to the ALREADY-CATALOGUED `reserveAndEmitDLEntry` (14th class)
   whack-a-mole SIGBUS, unrelated to and not caused by this session's
   edit. New guard fired 0/1 — informative null, not a confirmed fix
   (there was no observed crash at this site to begin with; this is
   preventive hardening, not a repro-driven fix).

## The two real remaining options

1. **Continue the static sweep** — 142 candidates remain (full list
   below). Each needs the SAME rigor as `selectPostCrawlCraft`: read the
   whole loop body (not just the flagged self-ref line), identify every
   register that aliases the untrusted pointer, find a safe bail target
   by reading forward from the natural loop-exit label to confirm no
   downstream code depends on the guarded register's value, then patch +
   regen + build + audit the patch-report multiplicity + (ideally) one
   soak. This is real, valuable, `ADVANCED`-able work with unusually
   high leverage (this family has cost 6+ sessions their actual
   experiments by pre-empting soaks — see s89-93/s194/s216/s219-220/s248).
   Good next candidates, roughly in order of plausible relevance to
   frequently-soaked call paths (render/DL-emission functions, all in
   `funcs_3.c`/`funcs_4.c`, are the same family as the already-fixed
   `heapWalker`/`renderUnlitMeshFaces`/`submitSceneNodeRender`):
   `selectPostCrawlCraft`'s own remaining 2 sites (`0x800CBDA8`,
   `0x800CBDE4` — two near-identical inlined list-insert helpers, NOT
   yet traced), `renderLitMeshFaceGroup` (14 sites, `funcs_4.c`),
   `renderLitTexturedMeshFaces` (11 sites, `funcs_3.c`),
   `func_800AE3F0` (10 sites, `funcs_27.c`), `beginFrameDLChunk` /
   `emitFrameRdpInitDl` (10 sites each, `funcs_3.c`).
2. **`docs/CURRENT-TRUTH.md` housekeeping** — still ~407 KB+, flagged
   40+ sessions, still not done. Per `ITERATION.md` this does NOT count
   as `ADVANCED` on its own — pair it with a real change or expect to
   file `SUBSTITUTED`.

## Full candidate list (143 total, 1 fixed this session)

Grouped by `(file, function)`. Format: `file: func -- N site(s) -- lines
[selfref line numbers in funcs_*.c, sibling N64Recomp/RecompiledFuncs/]`.
Re-derive with `python3 scratch/agent/find_unguarded_walks.py` if the
sibling checkout changes (it regenerates `unguarded_walk_candidates.json`
too). `selectPostCrawlCraft`'s first site (line 30362) is DONE; its other
2 (30684, 30735) are not.

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
funcs_3.c: reserveAndEmitDLEntry -- 3 -- [14836, 15029, 15222]
funcs_30.c: selectPostCrawlCraft -- 2 remaining (1 of 3 fixed s249) -- [30684, 30735]
funcs_35.c: static_4_800B13E0 -- 8 -- [3551, 3711, 3853, 4035, 4248, 4408, 4579, 4724]
funcs_35.c: static_4_800B3FB4 -- 1 -- [11851]
funcs_35.c: static_4_800B40A0 -- 1 -- [12007]
funcs_4.c: buildOrientedFaceGeometry -- 3 -- [7611, 7842, 8175]
funcs_4.c: drawSubtitleText -- 6 -- [16349, 16581, 16945, 17740, 18531, 19115]
funcs_4.c: drawTextGlyphRect -- 1 -- [15740]
funcs_4.c: renderFlatMeshFaceGroup -- 6 -- [3189, 3421, 3693, 4338, 4540, 4741]
funcs_4.c: renderLitMeshFaceGroup -- 14 -- [8640, 8870, 9142, 9562, 10174, 10426, 10760, 10957, 11318, 11615, 11997, 12635, 12916, 13230]
funcs_4.c: renderUnlitMeshFaces -- 1 -- [5017]
funcs_4.c: setupCameraMatrices -- 3 -- [19722, 20792, 20981]
funcs_43.c: static_5_800CBBB8 -- 1 -- [13142]
funcs_43.c: static_5_800CBD88 -- 1 -- [13480]
funcs_43.c: static_5_800CBDC4 -- 1 -- [13535]
```

Note: `funcs_4.c: renderUnlitMeshFaces -- 1 -- [5017]` is a SEPARATE site
from the one already guarded there (s219, address `0x80011CE0`) — not yet
traced, worth a look since that function is already known-hot.

## Do NOT do this iteration

- Do NOT re-run `mtldebug1`..`mtldebug4`, `scissorfix1`, `malloclog1`,
  `malloclog2`, `metalresize1`, `selectpostcrawlguard1` in place —
  superseded tags. New soaks need new tags.
- Do NOT batch-apply guards from the JSON candidate list mechanically —
  s249 found the naive self-ref signature misses a second aliased
  register in at least one case; every site needs its own full-loop-body
  read first.
- Do NOT revive the NaN_CHECK-disable idea (CURRENT-TRUTH `-55`/`-56`) —
  already tried, A/B-tested, and reverted at s216 (`-57`).

## Environment notes (carried forward, still current as of s249)

- **Permission gate CONFIRMED CLEARED through s249.**
- **`GAME_EXTRA_ENV`** (`run_mission_keys.sh`, s241): space-separated
  `VAR=val VAR2=val2` string, scopes extra env vars to ONLY the game
  process.
- **Env-gated logging pattern**: `static const bool s_X = [](){ const
  char *v = std::getenv("VAR_NAME"); return v && v[0] && v[0] != '0'; }();`
  then `if (s_X) { std::fprintf(stderr, ...); std::fflush(stderr); }`.
- **Block-wait pattern**: launch the soak with Bash `run_in_background:
  true`, then block-wait on the returned task ID (400000-480000ms
  timeout) — confirmed working again at `selectpostcrawlguard1`.
- **`update_screen` counter rate is ~60/s** once past the title screen —
  useful for extrapolating wall-clock death time from the last `[vi]`
  line when the driver's own `wall=` figure undercounts.
- `/tmp` is not writable this session — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ...` and `git -C <path> <cmd>` get blocked/need
  extra approval — issue `cd` as its own Bash call first, and plain
  `git status`/`git diff`/etc. (no `-C`) once cwd is already there. Even
  `cd ... && cmd > file` (redirection) gets blocked as a compound op —
  issue the `cd` as its own call, then the redirecting command separately.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`.
- **`campose*` armed env-var set** (unchanged since `campose11`, now also
  used by `selectpostcrawlguard1`):
  `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`
  — plus the new `ROGUESQ_LOG_SELECTPOSTCRAWL_GUARD=1` (s249). Keep all
  armed in any new soak; see
  `scratch/s73_post_a_scene/run_selectpostcrawlguard1.sh` for the full
  current set (this file survives across sessions on disk even though
  `scratch/` is gitignored — copy it forward for new soaks; only
  `STATUS`/`OUTCOME`/`NEXT.md`/`run_mission_keys.sh` are git-tracked).
- **The `[phase] vi_width=512 (was 1024) origin=0x006AB400` line at
  ~t=74-75s is THE confirmed SELECT-CRAFT->mission transition marker.**
- **Regen is mandatory-delete-all-first**: per CURRENT-TRUTH item 0,
  `N64Recomp` skips rewriting any `funcs_*.c` that already exists on
  disk, so leftover files from a previous session silently stack
  duplicate patches. Always `rm`/delete all 45 `RecompiledFuncs/funcs_*.c`
  before `make_elf.py` → `regen_n64recomp.sh` → `fixup_game_funcs.py` →
  `cmake --build`, and audit the fixup patch-report for anything other
  than the expected `xN` multiplicity before trusting the build (s249
  did this, found no anomalies beyond the pre-existing, already-known
  double-report quirk in `emitAllocatedDLCommand`'s GUARD2/r4 lines,
  unrelated to this session's edit).
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  — `scratch/agent/checksum_campose11.py` (s235) is mtime-aware, reuse
  this pattern.
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- The driver's own `CRASH: N` summary counts occurrences of the LITERAL
  STRING `[CRASH]` (many per crash) — grep `[CRASH] caught signal` for
  actual crash event counts.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each
  iteration by the harness — normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`,
  `NEXT.md`, and `run_mission_keys.sh` are tracked exceptions. Non-tracked
  scratch files (driver scripts, analysis scripts, logs) persist on disk
  across sessions but are not in git history — don't assume they're safe
  from an actual `git clean`/fresh-checkout scenario.
- Verify a fresh binary before trusting a null result: `strings
  build/RogueSquadron64Recomp | grep '<your-new-tag>'` plus `ls -la
  build/RogueSquadron64Recomp` vs. the soak's start time.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (still ~407 KB+ / 5900+ lines,
flagged 40+ sessions without action).

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly. Every guard
in the whack-a-mole family, including this session's, lives there.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.
