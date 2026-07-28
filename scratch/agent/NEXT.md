# NEXT work unit — densify capture across the STAR WARS-logo/crawl window and find the crash blocking it

s151 found a genuinely NEW post-hangar scene for the first time in ~150
sessions — read PORTING-STATE's Session 151 entry before doing anything
else; this file only has the actionable summary.

## What s151 did and found

Planned work unit was validating 2 new `composeNpcOrientationMatrix`
guards (3rd/4th unguarded table-deref sites, landed and built clean).
The soak (`composeguard3`) never reached that function (0 entry logs,
guards unvalidated either way) — but survived far longer than any prior
soak in this family (hold-iter 26/30 vs. the usual hold+1-17s), and its
own screenshots show something never seen before: a **"STAR WARS" logo**
(same asset as the game's own boot sequence) growing/zooming across
`hold_13`→`hold_17`, fading to black by `hold_22`, then crawl-text-like
glyph fragments streaking across `hold_24`/`hold_25`
(`scratch/s73_post_a_scene/composeguard3/`).

**Independent confirmation**: the `[phase] vi_width` log shows a
transition to width 640, origin **`0x006A2900`** at t=142.4s — the
first-ever novel VI origin in this whole investigation (not outdoor
`0x690400`, not war-room/craft-select `0x6AB400`, not any boot origin)
— timed almost exactly to the `hold_24`/`hold_25` frames. Two
independent lines (visual + VI-origin) converge: a real, new scene
started playing.

**Not yet resolved**: whether this is a genuine per-mission intro
cinematic (Star Wars logo + opening crawl, movie-style) or an errant
jump into replaying stale boot-sequence scene-graph data. Both are
consistent with what was observed so far.

The crash that ended it (SIGBUS, backtrace `processSceneNode + 7640` ←
`traverseSceneGraphRecursive` ← `setupCameraMatrices` ←
`static_5_800C9BF0` ← `menuOverlayInit` ← `mainGameLoop`) is NOT
confirmed to be the already-catalogued 14th class (`reserveAndEmitDLEntry`)
— `emit-dl-guard2`/`3` were armed and did not fire, but the backtrace
shape is similar enough (both run through `submitSceneNodeRender`/
`processSceneNode`) that an inlined/misattributed match is plausible.
Not resolved this session.

## Do next

1. **Densify capture across the new window.** Copy
   `run_composeguard3.sh` forward (it already has the full diagnostic
   battery + the new guard3/guard4 flags armed — keep them, they're
   free). The existing `CAPTURE_TICK_S=0.2` only densifies the
   post-Start-press window (`after_p1_start_*.png`), not the `hold_*.png`
   captures (1 Hz) where the STAR WARS logo/crawl actually appeared.
   Check `scratch/s73_post_a_scene/run_mission_keys.sh`'s hold loop for
   whether it respects `CAPTURE_TICK_S` too, or whether that needs a
   small edit to densify JUST the hold window (the logo/crawl content
   is between hold_13 and the hold_26 crash — roughly hold+13s to
   hold+26s wall-clock). If editing `run_mission_keys.sh`, keep the
   change backward-compatible (default unchanged) like the s150
   `CAPTURE_TICK_S` addition.
2. Read the densified frames yourself before writing anything up — do
   not delegate the visual read for a claim this significant. Try to
   actually transcribe the crawl text if the higher tick rate resolves
   it; that alone might identify which mission this is.
3. **Find and guard the crash site.** Source-read `processSceneNode`
   (`0x80014FA0` per `symbol_files/main_overlay.txt`, "per-node body of
   traverseSceneGraphRecursive... registers node into a render-queue
   table... dispatches between 3 render-state branches that each call
   submitSceneNodeRender") in the regenerated
   `N64Recomp/RecompiledFuncs/funcs_*.c` — grep for its guest address to
   find the file (funcs_40.c is a reasonable first guess given its
   neighbors, but do not assume). Compare its actual compiled size to
   the crash's `+7640` byte offset — if the real function is much
   smaller than 7640 bytes, the crash is almost certainly in a
   *different*, subsequent function misattributed to the nearest
   preceding symbol (same caveat as the 10th/18th classes) — grep
   forward from processSceneNode's start to find what actually sits at
   that offset. Apply the same guard template as compose-npc-orient's
   guards (bounds-check `0x80000000-0x80800000`, `getenv`-gated log,
   bail to the function's own real epilogue) at whatever unguarded
   dereference is actually there.
4. Full regen + soak with the new guard armed, same battery. Discriminating
   outcome: does the process survive past where this crash previously
   landed? If yes and a new scene (not logo/crawl, not hangar) appears,
   that's likely the actual mission/flight scene — M3 close. If it loops
   back to title/boot, that answers the cinematic-vs-erroneous-jump
   question the other way.

## Do not

- Do not re-treat "composeNpcOrientationMatrix guard3/guard4 validated"
  as done — 0/0 this run, still needs a positive control (a soak where
  the function is actually reached).
- Do not assume the STAR WARS logo scene is definitely a real mission
  intro — it's equally consistent with an erroneous jump into stale
  boot scene-graph data. Get more evidence (denser capture, ideally
  readable crawl text or a scene after the crawl) before calling this
  in either direction in CURRENT-TRUTH.
- Do not assume `processSceneNode`'s crash is the already-catalogued
  14th class (`reserveAndEmitDLEntry`) without checking — the
  `emit-dl-guard2`/`3` flags were armed and silent, which is evidence
  against, not for, that identification.
- Do not re-run `fixup_game_funcs.py` twice without a full regen between
  runs — verify via grep that any patch you land fired exactly `x1`
  before building.

## This session's environment notes (carry forward, still current)

- **A soak's own screenshots are free evidence, including at 1 Hz — this
  session's biggest finding (the STAR WARS logo) was visible even in
  the un-densified `hold_*.png` captures.** Always read the full set of
  a soak's screenshots before writing conclusions, not just the last one
  or two before a crash.
- **A crash's own backtrace is evidence about game state, not just a
  bug to fix** — but a "nearest symbol + large offset" attribution
  should be treated as unconfirmed until the actual function size is
  checked (this session left that unresolved for `processSceneNode`).
- VI-phase tracking (`[phase] vi_width=...`) **can** discriminate scenes
  when the value is genuinely novel (never seen before across the whole
  investigation) — the s48/s150 caveat is about scenes that *share*
  known VI parameters, not about ruling out VI evidence entirely.
- `CAPTURE_TICK_S` (added s150, `run_mission_keys.sh`) only applies to
  the post-Start-press probe-wait loop, not the separate hold-window
  capture loop — check both loops before assuming a densify request
  actually took effect.
- Function/line-number estimates in NEXT.md/PORTING-STATE drift a few
  lines every regen — always grep/read the actual regenerated file
  before writing a regex anchor or planning a reorder.
- N64Recomp's codegen convention for a fixed-global access: writes are
  `MEM_W(<offset>, ctx-><base>) = ctx-><src>;`; reads flip the argument
  order to `ctx-><dst> = MEM_W(ctx-><base>, <offset>);`.
- `caller_ra` (`ctx->r31` at function entry) reads `0x00000000`
  universally — stop treating it as a signal (s92, s139-141).
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns — use a `python3 -c` one-liner with `pathlib.Path.glob()`.
- Do NOT re-run `fixup_game_funcs.py` a second time in the same session
  without a full regen first (non-idempotent, s102) — delete
  `RecompiledFuncs/funcs_*.c`, re-run `make_elf.py` (cwd
  `~/Documents/Tools/rogue_squadron64`), then
  `zsh tools/agent/regen_n64recomp.sh` (cwd this repo, NOT `N64Recomp`),
  THEN `fixup_game_funcs.py` once (cwd `N64Recomp`) — verify by grepping
  the regenerated `.c` directly.
- `cmake --build` needs cwd `build/` and
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` for Metal
  shader rebuilds.
- Write a new wrapper script file per soak tag (`scratch/agent/run_
  <tag>.sh`) rather than parametrizing a single reusable script via env
  indirection. `run_composeguard3.sh` (this session) is a good template.
- Launch the soak via `zsh <absolute-path>/run_<tag>.sh > <absolute-path>/
  run_<tag>_driver.log 2>&1` as a `run_in_background` Bash call, then
  block synchronously with `until ! pgrep -f "./RogueSquadron64Recomp"
  >/dev/null 2>&1; do sleep 5; done` before closing out the iteration.
- Checking submodule (`lib/...`) git status needs `env GIT_DIR=lib/X/.git
  GIT_WORK_TREE=lib/X git status --short`, or a plain `cd <absolute
  path>` as its own command followed by a separate `git status` call.
- Output redirection (`>`) from Bash is sandboxed to the session's
  allowed working directories — target `scratch/agent/`, not `/tmp`.
- Prefer a single `python3 script.py` file (Write then run) for
  multi-step log analysis instead of a bash heredoc.
- This fix lives entirely in the sibling `N64Recomp` checkout
  (`fixup_game_funcs.py` + regenerated `RecompiledFuncs/*.c`), not
  `lib/` — no `submodule-patches/export.sh` step needed for it.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target — migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment. Flagged for many
sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-151 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
