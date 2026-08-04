# NEXT work unit — identify the TRUE call site(s) of tickAudioSequencerFrame/tickAllActiveSongs

## Context — s316 found the 3-gate-copy model is contradicted by direct measurement

s316 instrumented all 3 near-identical countdown gates inside `musyxSynthFrame` (`RecompiledFuncs/
funcs_24.c`, gate1 ~0x80091474, gate2 ~0x80091534, gate3 ~0x800915E8 — s107's "3 near-identical gate
copies", the ONLY static call sites to `tickAudioSequencerFrame`/`tickAllActiveSongs` anywhere in
`RecompiledFuncs/*.c`, grep-confirmed). Result: **none of the 3 gates ever takes the "call" branch** in
a full 600s soak — gate1 40/40 samples `taken_skip=1`, gate2 only 4/40 iterations reached at all (all
`taken_skip=1`), gate3 **0 samples** (its containing code path never reached once). Yet
`tickAllActiveSongs`'s own independent entry counter (`[reach-allsongs-entry]`) confirms **37 real
calls** happened in the same run. The only known call sites, sampled exhaustively, account for zero of
the 37 observed calls. Full detail: `docs/CURRENT-TRUTH.md` item -175, `PORTING-STATE` Session 316.

## The work unit

**Find the TRUE call site(s) that produce the 37 real calls to `tickAllActiveSongs`/
`tickAudioSequencerFrame`, directly, without relying on the countdown-gate model.**

1. Add a diagnostic at `tickAudioSequencerFrame`'s own entry (`RecompiledFuncs/funcs_23.c`, function
   starts at guest address visible in the `RECOMP_FUNC void tickAudioSequencerFrame(...)` header) that
   logs `ctx->r31` (the `$ra` register — MIPS return address) alongside the existing entry counter `n`.
   Use the same `n<40||(n%128)==0` cap convention and `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN` env gate as the
   existing `[tick-audio-seq]` diagnostic (or extend that existing patch in place — cheaper than a new
   one, check `fixup_game_funcs.py` line ~1999 `_tick_audio_seq_patch`).
2. Compare the logged return addresses against the 3 known call sites' post-call addresses:
   gate1 → `0x800914A4`, gate2 → `0x80091568`, gate3 → `0x8009161C` (the instruction immediately after
   each `jal` to `tickAudioSequencerFrame`, per s316's source-read). If most/all of the 37 calls return
   to one of these 3 addresses, the gate model is right after all and s316's contradiction is itself an
   artifact (check for a diagnostic placement/ordering bug in the gate2/gate3 patches before trusting
   this outcome — a positive control the s316 soak didn't have). If the calls return to NONE of these 3
   addresses, that directly proves a 4th, unlocated call site — most likely an **indirect/function-
   pointer call**, mirroring s310's finding that `musyxSynthFrame` itself is invoked through a 4-slot
   VI-retrace callback table rather than a direct textual call (a plain grep would miss an indirect call
   the same way it missed that one). In that case, search for a callback-table/function-pointer pattern
   near `tickAudioSequencerFrame`'s address being stored/loaded, the same way s310 traced
   `musyxSynthFrame`'s.
3. Batch this into the same soak as anything else this session wants measured (iron rule 6). Reverse
   `setDisplayMode`'s site (0x8008EB40, `RecompiledFuncs/funcs_23.c`, hand-edit `= 0;` to `= ctx->r2;`)
   a 10th time to match run conditions, one full soak with all breadcrumbs armed (copy
   `scratch/s73_post_a_scene/run_step316gate23.sh` as the template — newest, confirmed working), read
   the result, **revert the site again same session** (mandatory — deterministic boot hang if shipped
   reversed). Confirm `MEM_B(0XF50, ctx->r1) = 0;` is restored before ending session.
4. Regen if this touches `RecompiledFuncs/*.c` content: `fixup_game_funcs.py` edit → clear
   `RecompiledFuncs/*.c` → `N64Recomp/build/N64Recomp rogue_squadron.toml` → `python3
   fixup_game_funcs.py` → `cmake --build build -j8`.

**Discriminating outcome**: if the logged `$ra` values match one of the 3 known gate return addresses,
the gate model survives and s316's contradiction needs a narrower explanation (re-check the gate2/gate3
diagnostic placement for a bug before concluding the model is right — that's the more likely fix if this
branch is taken). If the `$ra` values match NONE of the 3, a 4th call site (near-certainly indirect) is
proven to exist and becomes the new target — this would be a second instance of the exact indirect-call
blind spot s310 found for `musyxSynthFrame`, worth flagging as a pattern (grep-based call-site inventories
in this codebase have now missed an indirect call twice).

## Environment notes (carried forward, all still valid)

- Regen paths for game-code patches are in `/Users/williambuckley/Documents/Tools/N64Recomp`
  (`fixup_game_funcs.py`, `RecompiledFuncs/*.c`, `build/N64Recomp`, `rogue_squadron.toml`), NOT this
  repo (`~/Documents/Tools/RogueSquadron64Recomp`). This is a SEPARATE checkout from
  `lib/N64ModernRuntime`'s nested `N64Recomp` submodule (confirmed s316: different `.git`, different
  `RECOMP_FUNCS_DIR` in `CMakeLists.txt` points at `${CMAKE_SOURCE_DIR}/../N64Recomp/RecompiledFuncs`,
  i.e. the standalone sibling directory) — edits here do NOT need `submodule-patches/export.sh`. Only
  edits actually inside this repo's `lib/` need that.
- `cd` into `N64Recomp` FIRST as its own bare `cd` command, THEN run `./build/N64Recomp
  rogue_squadron.toml` with output redirection in a SEPARATE Bash call — combining `cd` and a redirect
  in one compound command triggers a permission prompt in this sandbox. Same for any cd+redirect combo.
- `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`
  clears RecompiledFuncs (use the ABSOLUTE path).
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from this repo's
  root — allowlisted verbatim, works as a single command.
- Soak driver template: `scratch/s73_post_a_scene/run_step316gate23.sh` (now the newest; copy it, don't
  hand-roll — it's `run_step315audtaskcap.sh` with the name substituted, same breadcrumb set).
- Launch the soak via Bash with `run_in_background: true` (cd into `scratch/s73_post_a_scene` first as
  its own bare command), then `TaskOutput` with `block: true` and `timeout` up to 600000ms — do NOT
  foreground-poll. The soak's own 600s phase-timeout exits nonzero (exit 5, INCONCLUSIVE) on the
  expected deterministic hang — that's success for this soak design, not a tooling failure; the game
  process is killed automatically. Confirm `pgrep -f "build/RogueSquadron64Recomp"` is empty before AND
  after.
- `/tmp` is blocked for redirects — use a path inside this repo, `N64Recomp`, or `rogue_squadron64`
  instead.
- `scratch/s73_post_a_scene/step316gate23/run.log` (743 KB) is s316's saved log if a future session
  wants to re-verify the 40/4/0/37 sample counts before building anything new.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang (same slug, s303-316 — still the active
investigation thread. 10 of these sessions have each produced a discriminating result in sequence
(s303/s306/s307/s309/s310/s311/s312/s313/s315/s316), resetting the iron-rule-8 no-progress counter every
time; s314 (maintenance) doesn't count. Continue the same slug next non-maintenance session.)
