# NEXT work unit

## s351 landed: guarded the write-through-v1 sibling of s350's read guard (2nd landed fix
## in `drainMeshReleaseQueue`'s tail-scan idiom)

Full detail: `docs/CURRENT-TRUTH.md` item -207, `PORTING-STATE` Session 351. Short version:

- Drained `s350_drainmeshguard_verify1/2.sh` (loop had already run + moved them to `soak_queue/done/`).
  `verify1`: CRASH at `drainMeshReleaseQueue+1580`, `last-guest-pc=0x800081c4`, **with the s350 read
  guard confirmed firing in the same run** (`guard_fire_n=1`, `bad_v1=0x00010001`) — the read guard
  bailed correctly but didn't repair `ctx->r3` (v1) itself, and the function unconditionally writes
  through that same pointer 2 lines later. `verify2`: CRASH at a 4th distinct symbol
  (`static_5_800AAD9C+5140`), not informative for this guard.
- Guarded the write-through-v1 site (`~/Documents/Tools/N64Recomp/fixup_game_funcs.py`, both
  compiler-duplicated `0x800081C4` occurrences, one indent-agnostic regex). New tag
  `[drain-mesh-write-guard]`, reuses the already-armed `ROGUESQ_LOG_DRAIN_MESH_TAIL_GUARD` env var.
  Full regen + rebuild clean (`patched x2`). Queued `s351_drainmeshwriteguard_verify1/2.sh`.
- `HYPOTHESIS-ID m5-audio-destub-drainmesh-breadcrumb` CLOSED (2nd landed fix, same pattern as
  s348→`m5-audio-destub-contentguard-verify`). New thread:
  `m5-audio-destub-drainmesh-writeguard-verify`.

## The work unit: drain `s351_drainmeshwriteguard_verify1/2`, read whichever landed

**Step 1**: `tail -10 scratch/agent/SOAK-RESULTS.md`. The loop drains up to 2 recipes between
iterations, so both may already be done, or run them yourself the same way (`zsh
scratch/agent/soak_queue/s351_drainmeshwriteguard_verify1.sh` — NOT `bash`, it isn't allowlisted).

**Step 2 — read each result**:
- `write_guard_fire_n` > 0: the write guard is firing (positive control — the invalid-v1-at-write-site
  case is real). Check `[drain-mesh-write-guard]` log lines for `bad_v1` values — same value/small
  range repeatedly is a lead on the corruption source; scattered is more consistent with generic
  memory-storm noise.
- `crash_markers=0` (CLEAN) in both: weak evidence this closes the site; n=2 is thin given the parent
  hypothesis's known high crash-symbol variance — note it, don't over-claim.
- Still crashes at a NEW `drainMeshReleaseQueue` offset (e.g. the still-unguarded `0x800081C8`
  `MEM_W(0X4,ctx->r2)=ctx->r3` sibling, where `ctx->r2` not `ctx->r3` is the address operand — different
  idiom, would need its own guard if `ctx->r2` itself turns out corrupted): that's the next site to
  localize/guard — BREADCRUMB15 already covers the whole function, so `last-guest-pc` will be precise
  immediately.
- Crashes elsewhere entirely (a 5th distinct symbol): further supports the diffuse-storm framing. At
  that point, per s350/s351's own escalation note, the higher-value move shifts from guarding individual
  sites to a heap-corruption-storm audit of the parent hypothesis (item -203) — is there a common
  upstream root cause (e.g. a use-after-free or buffer overrun elsewhere writing garbage into whatever
  memory `drainMeshReleaseQueue`/other dense pointer-chase functions happen to walk next)? This is a
  legitimate pivot per the M5-AUDIO-PLAN step-5 checkpoint, not a rule violation.

**Step 3 — budget check**: this is iteration 1 of the NEW thread `m5-audio-destub-drainmesh-writeguard-
verify` (the prior thread closed with a landed fix, budget resets). If this iteration's result doesn't
discriminate cleanly (more scatter, no clean signal), that's fine for iteration 1 — queue one more
verify round. Only escalate to the pivot/BLOCKED path if this becomes iteration 3 with still no signal.

Separately, the PARENT hypothesis `m5-audio-destub-step5-crashrate-comparison` (item -203) is on its
own budget: this next iteration is its LAST before the 3-strike rule forces a pivot check on it too — if
whichever thread you work still reads as diffuse-not-concentrated afterward, write up the
heap-corruption-storm-audit reframing explicitly rather than queuing another single-site verify round.

## Environment notes (carried forward — see s327-351 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked, and
  confirmed s351 to sit entirely outside this repo's `lib/`/submodule-patches system). Delete
  `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Full regen order: `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` ->
  `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` ->
  `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` ->
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j8`. Run each step as its own
  single command (compound `cd a && cmd` sometimes needs manual approval this session).
- `soak_queue/*.sh` recipes must be invoked as `zsh scratch/agent/soak_queue/<name>.sh` if you need to
  drain one yourself — `bash <path>` is NOT allowlisted even though the recipe files start with a
  `#!/bin/bash` shebang; only `zsh:*` is in the allow rules. If you drain a recipe manually, also
  manually do what `run_soak_queue()` normally does: save output to
  `scratch/agent/soak_results/<name>_<timestamp>.log`, append a line to `SOAK-RESULTS.md`, move the
  `.sh` to `soak_queue/done/`.
- `nm` itself needs explicit interactive approval — `python3 -c "..."` wrapping `subprocess.run(['nm',
  ...])` IS allowed. `scratch/agent/check_symtab3.py` is the latest template for "is this crash symbol
  genuine or nearest-symbol misattribution."
- **All BREADCRUMB* passes share ONE `g_rs64_last_guest_pc` global.** `drainMeshReleaseQueue`
  (BREADCRUMB15, s349) is fully instrumented — its `last-guest-pc` is always precise. If a crash's
  `last-guest-pc` doesn't look like it belongs to the crashing `pc-symbol` function, check first whether
  that function is even breadcrumbed.
- `run_s327waitpump.sh` arms `ROGUESQ_LOG_DRAIN_MESH_TAIL_GUARD=1` by default (s350), which now covers
  BOTH `[drain-mesh-tail-guard]` (read site, s350) and `[drain-mesh-write-guard]` (write site, s351) —
  one env var, two diagnostic tags.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` — matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=<n> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`env` prefix required —
  project rule 10 / CLAUDE.md). Log lands at `scratch/s73_post_a_scene/<label>/run.log` — grep it,
  don't read it directly.
- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise, always trust for "what function crashed") and
  `[CRASH][last-guest-pc]` (a separately tracked guest checkpoint, only meaningful if the crashing
  function is breadcrumbed) answer different questions by design.
- `rc=137`/launcher timeouts don't necessarily mean a game-side hang — check the launcher log's own
  `done wall=Ns` line and `run.log` byte size before reading a timeout as a stall.

HYPOTHESIS-ID: m5-audio-destub-drainmesh-writeguard-verify (iteration 1 — opened s351). Parent:
m5-audio-destub-step5-crashrate-comparison (item -203, on its LAST iteration before the 3-strike rule).
