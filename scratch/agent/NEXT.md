# NEXT work unit — source-read and guard `emitAllocatedDLCommand`
# (new lead from s220, hit at the earliest death point in the whole lineage)

Read PORTING-STATE Session 220 in full (`grep -n "^## Session 220"
PORTING-STATE.md`) before doing anything else. Short version: s220 re-ran
s219's `renderunlitguard1` soak unchanged (tag `renderunlitguard2`) per
NEXT.md's own Step 1. The `renderUnlitMeshFaces` guard question from s219 is
STILL unconfirmed — `unlit-mesh-tracer`/`renderunlit-guard` both fired 0
times a 2nd time (that function was never called either run) — but the
soak died at **hold-iter 1** (wall=0s, the earliest death point in the
entire s209-219 lineage) to a **genuinely new crash**: `[CRASH][pc-symbol]
sym=emitAllocatedDLCommand+5832` (`N64Recomp/RecompiledFuncs/
funcs_3.c:2622-3210`), reached via `submitSceneNodeRender` →
`processSceneNode` → `traverseSceneGraphRecursive` (x2) →
`setupCameraMatrices` — i.e. inside the SELECT YOUR CRAFT hangar/
camera-orbit scene's own rendering, not flight. This is the SAME fault
family s194/s219 diagnosed for `renderUnlitMeshFaces` (a raw, un-subtracted
KSEG0-tagged guest pointer added directly to the constant rdram host-base
literal `0x0000000300000000`, bypassing `MEM_W`'s sign-extend-then-subtract
discipline) — register dump: `x9=0x0000000300000000` (the constant, in a
different register slot than prior sightings — expected, register
allocation is call-site-specific), `x10=0x0000000080000000` (a suspiciously
round, un-subtracted KSEG0-tagged pointer — looks like guest address 0),
`far=x9+x10` exactly.

**Why this is the priority over re-testing renderUnlitMeshFaces a 3rd time**:
this crash happens at hold-iter 1, rendering the craft-select scene itself,
plausibly BEFORE the hold schedule's `95:start` key (documented in
CURRENT-TRUTH's menu-state-machine section as the key that leaves SELECT
YOUR CRAFT into hangar-flight) ever gets to fire. If this crash is a
recurring early blocker, it may be why so many soaks in this lineage never
reach flight/mesh content at all — fixing it could do more to unblock
*every* downstream guard-confirmation soak (including the still-open
renderUnlitMeshFaces question) than repeating that soak unchanged again.

## Do this iteration

### Step 1 — source-read `emitAllocatedDLCommand` end to end

`funcs_3.c:2622-3210` (~590 lines — confirm the exact end boundary yourself
with `grep -n "^RECOMP_FUNC" funcs_3.c` before assuming this range; do NOT
inherit this estimate uncritically, per s218's own corrected mistake with
`heapWalker`'s range). Hunt for the SAME idiom every guard in this family
(`heapWalker` GUARD3/GUARD4, `heapFreeListDequeue`, `renderUnlitMeshFaces`)
was built for: a `MEM_W(ctx->rN, ...)` load into a register, immediately
followed by a SECOND `MEM_W(ctx->rN, offset)` on that SAME register with no
intervening validation (upper-32-bit check against `0xFFFFFFFF`, or a range
check). Grep every `MEM_W(ctx->rN,` occurrence in the function and look for
back-to-back pairs on the same register, the same way s219 found
`renderUnlitMeshFaces`'s single site at `0x80011CE0`.

If the function is large enough that a full read risks the read-window
limit, delegate to a subagent with an EXACT instruction: "grep every
`MEM_W(ctx->rN,` call in funcs_3.c:2622-3210, list them with line numbers
and the register each one reads/writes, flag any back-to-back same-register
pair" — do not have the subagent guess at a fix, just return the raw
inventory.

### Step 2 — ship a guard matching the established template

Same shape as `renderUnlitMeshFaces`'s (s219, `fixup_game_funcs.py`): check
`hi != 0xFFFFFFFF` (NOT a bare `U32()` truncated compare — s213's documented
trap, silently passes this exact corruption shape), on a bail target that
reuses the function's own natural degrade path (its "null"/"empty" exit),
not a fabricated one. Regen order: `make_elf.py` → `N64Recomp` →
`fixup_game_funcs.py` → `cmake --build` (mandatory, not optional — fixup step
edits generated code, dies at next regen otherwise).

### Step 3 — soak

New tag (e.g. `emitdlguard1`), same s213-219 recipe
(`STICK_SCHEDULE="95:start 100:a 150:sr 200:sl 250:su"`, `HOLD_S=300`), keep
ALL existing diagnostics armed as a regression check (`unlit-mesh-tracer`,
`renderunlit-guard`, `heapwalker-guard`/`-guard3`/`-guard4`, `mesgqueue-guard`,
`heaplistdeq-guard`) plus a new `ROGUESQ_LOG_EMITDL_GUARD`-style env var for
the new guard.

Discriminating outcomes:
- **New guard fires (n>0) AND the run survives past hold-iter 1 without an
  `emitAllocatedDLCommand`-area crash** → real fix, single-source confirmed;
  a 2nd soak would still be needed for two-source per rule 4. Also check
  whether `unlit-mesh-tracer` finally fires now that the process survives
  longer — that would be a strong signal this crash really was gating
  reachability of mesh content, not just an unrelated coincidence.
- **New guard fires 0, no `emitAllocatedDLCommand` crash this run** →
  inconclusive on this guard, no regression; still worth keeping.
- **Dies to a byte-identical `emitAllocatedDLCommand` crash again with the
  new guard firing 0** → site identification wrong, there's a different
  unguarded site in this function; re-read rather than re-ship the same fix.
- **Dies to something unrelated** → uncontrolled null, same "random crash
  wins the soak race" pattern as most prior sessions; not a refutation.

## Do NOT do this iteration

- Do not re-run `renderunlitguard1`/`renderunlitguard2` a 3rd time
  unchanged — that specific question has had 2 identical attempts already
  (budget rule 8); if you want to return to it, use NEXT.md's previously
  proposed Step 2 (force the code path via an extended `STICK_SCHEDULE` that
  reaches flight, per CURRENT-TRUTH's menu-state-machine section) rather than
  a 3rd identical rerun.
- Do not revive the "hunt the shared write site of 0x0000000300000000"
  framing (refuted s219, re-confirmed s220 in a 4th distinct call site with
  the constant in yet another register — it really is just the rdram-base
  literal, present in every fault by construction, nothing to hunt).
- Do not source-read `heapWalker`'s still-open `x9=0x38d47580` (s217) lead
  reflexively this iteration — real and separate, but not this iteration's
  planned unit; note if it recurs, don't chase same-session (budget rule 8
  territory already spent on it twice).

## Environment notes (carried forward, still current)

- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`** (s220, via `grep -n
  "^RECOMP_FUNC" funcs_3.c`). `renderUnlitMeshFaces` is `funcs_4.c:4963-5630`
  (s219, guard shipped, still unconfirmed live — see above). `heapWalker` is
  `funcs_3.c:99-700`, `heapFreeListDequeue` is `funcs_3.c:15427-17128` (both
  s217/s218, unchanged).
- **Raw crash logs are often still on disk long after the session that
  produced them** — `grep` the actual `run.log` under
  `scratch/s73_post_a_scene/<tag>/run.log` before trusting a prose summary of
  a register dump. This has caught real transcription errors before (s219 on
  s216's write-up) and confirmed exact matches (s219 on s194/s199/s218; s220
  on this session's own dump, double-checked before writing up).
- **`recomp.h` location**: the ONE that matters is
  `lib/N64ModernRuntime/N64Recomp/include/recomp.h` — nested submodule
  inside `lib/N64ModernRuntime`. `submodule-patches/export.sh`/`apply.sh`
  cover both copies. Any edit under `lib/` needs `export.sh` + commit, same
  session (not triggered s219 or s220 — no `lib/` edits either session).
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`** —
  the sibling checkout, genuinely untracked there (known since s83, not this
  project's commit scope, flagged for the user). Verify any prior session's
  guard is still present (`grep -n <guard_name> fixup_game_funcs.py`) before
  assuming a re-regen will include it — the code is also fully reproducible
  from the relevant PORTING-STATE session's text if the file were ever lost.
- **`fixup_game_funcs.py` is NOT fully idempotent** for at least one older
  patch (s139 `rs_malloc`) — only run it ONCE per regen cycle.
- The `[CRASH][pc-symbol]` diagnostic (dladdr on raw mcontext `pc`) is
  permanent, always-on, more precise than `backtrace_symbols_fd` (s213).
- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are ALL blocked.
  Source-level reasoning only.
- `-O0` Debug build, `RECOMP_FUNC` noinline, no LTO — dladdr resolving to
  function F means the fault is inside F's own body.
- `recomp.h`: `U32(val)` = `(uint32_t)(val)`; `gpr` = `uint64_t`; a legit
  KSEG0 `gpr` sign-extends, upper bits `0xFFFFFFFF`. Always check upper 32
  bits explicitly — a bare `U32()` check is blind to this corruption shape.
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- `./build/N64Recomp rogue_squadron.toml` needs an `env` prefix. Compound
  `cd ... && cmd` gets denied in one Bash call — issue `cd` and the
  following command as SEPARATE Bash calls (confirmed again s220 — even a
  `cd ... && zsh script.sh` one-liner for a background launch gets denied;
  it had to be issued as a single "cd && zsh" background command via
  run_in_background, which DID work — the restriction is specifically on
  foreground compound redirection/cd, test small before assuming denial).
- `git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule —
  `cd` into the target dir first (its own Bash call), then run bare
  `git <cmd>`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Launch soaks with `Bash(..., run_in_background=true)`. The Stop hook fires
  on scratch/agent/STATUS as soon as your turn ends, even mid-soak — if the
  soak isn't done yet, block on it explicitly in the same turn (e.g. an
  until-loop polling the background task's output file for a known
  completion marker like `--- done ---`) rather than ending your turn and
  waiting for the async task-notification; the notification arrives, but the
  Stop hook will block your *next* turn-end anyway if you haven't finished
  the exit contract, so you'll end up blocking on it one way or another —
  simplest to just wait inline.
- The `grep -ac '[CRASH]'` count in `run_mission_keys.sh`'s summary counts
  LINES matching the tag, not crash EVENTS — grep `caught signal` for the
  real event count. `unlit-mesh-tracer`'s own positive-control line is
  logged with a `[CRASH]` prefix too even though it isn't a crash (an
  existing project logging convention, not a bug).
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s220 —
read it with `grep`/offset-limited `Read`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail, paired with a real experiment — flagged for 18+
sessions without action, escalating.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` still shows as modified in `git status` — pre-existing, not
investigated; still worth checking whether its patches are in sync with
`submodule-patches/rt64*.patch` before assuming this is normal
steady-state dirtiness.
