# NEXT work unit — instrument `initN64RspMixer`'s countdown/period write, find the true reset mechanism

## Context — s317 refuted the "4th call site" hypothesis, found a 4th WRITE site instead

s317 tried logging `ctx->r31` ($ra) at `tickAudioSequencerFrame`'s entry to identify which of the 3 known
gates (`musyxSynthFrame`, `funcs_24.c` ~0x80091474/0x80091534/0x800915E8) fires the 37 real calls s316
found unaccounted for. **That approach was a dead end by design**: this recompiler translates direct
`jal`s into plain C function calls and never writes `ctx->r31` at the call site — `ctx->r31` only carries
real data right after code that explicitly assigns it (a stack-restore, or an indirect-call trampoline
computing a real return address). All 37 samples read `ra=0x00000000`, which is uninformative, not a
discriminating result.

Redesigned cheaply with pure grep (no build): searched ALL of `RecompiledFuncs/*.c` for both direct calls
to `tickAudioSequencerFrame` and any data reference to its guest address (0x8008D960, the pattern that
found `musyxSynthFrame`'s own indirect invocation in s310). Found exactly the same 3 known call sites,
zero others. **This definitively refutes the "4th/indirect call site" hypothesis** — unlike
`musyxSynthFrame`, `tickAudioSequencerFrame` truly has no other entry point in the recompiled codebase.

Whatever produces the 37 real calls MUST originate from one of the 3 known gates. Since s316 measured
all 3 gates taking 0 "call" branches in the same run the 37 calls happened in, **the gates' own countdown
state must be getting reset by something outside the 3 gates' own read/decrement/reload logic** — this
is now the live hypothesis.

**New lead**: grepping all writes to the shared countdown (`G_BASE-0x68EC`) beyond the 6 known gate
writes (2 per gate: decrement-store, reload-from-period) found a 7th write at `funcs_24.c:4706`/`4710`
(guest 0x80091A84/0x80091A8C), using `ctx->r3` — a different source register from all 6 gate writes
(`ctx->r2`), confirming a genuinely separate code path. This write sets BOTH the countdown and its period
to the same computed value (derived from an `mfc1`+bit-math sequence starting at guest 0x80091A68 — looks
like a float-to-fixed-point rate/divisor conversion). It's inside `initN64RspMixer`
(`funcs_24.c:4367`) — an init-sounding function name, so NOT yet confirmed to run per-frame (it would need
to, or be called very frequently, to explain gate1's countdown reading exactly 0 on all 40 samples across
one 600s run — an init-once write wouldn't keep re-resetting it).

## The work unit

**Confirm or refute whether `initN64RspMixer`'s countdown/period write is what keeps gate1/2/3 from ever
accumulating to a "call" state.**

1. Source-read `initN64RspMixer` in full (`RecompiledFuncs/funcs_24.c`, starts line 4367) to determine
   its caller(s) and call frequency — is it called once at boot, or from a per-frame/per-tick path? Grep
   `initN64RspMixer(rdram` across `RecompiledFuncs/*.c` for its own call sites first (cheap, no build).
2. If it's plausibly per-frame or high-frequency: add a counter+value diagnostic at guest 0x80091A84 (the
   write itself), reusing the `n<40||(n%128)==0` cap and `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN` env convention
   this whole lineage uses. Log call index and the computed `ctx->r3` value being written into both
   countdown and period.
3. Batch this into the same soak as the existing gate1/gate2/gate3/tick-audio-seq diagnostics (all still
   armed via `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1` in the soak driver — no new env var needed). If
   `initN64RspMixer`'s write fires between every gate1 read (interleaved in the log by line order), and
   writes a value that keeps landing gate1's countdown back near/at 0, that's the mechanism. If it fires
   only once near the top of the log (boot-time init) and never again, it's ruled out and the reset must
   come from `funcs_32.c:29181`'s still-unclassified `-0x68EC` reference (check read-vs-write there next —
   also cheap, no build, just read the surrounding lines) or somewhere not yet grepped.
4. Reverse `setDisplayMode`'s site (0x8008EB40, `RecompiledFuncs/funcs_23.c:9788`, hand-edit `= 0;` to
   `= ctx->r2;`) an 11th time to match run conditions, one full soak with all breadcrumbs armed (copy
   `scratch/s73_post_a_scene/run_step317ratrace.sh` as the template — newest, confirmed working), read
   the result, **revert the site again same session** (mandatory — deterministic boot hang if shipped
   reversed). Confirm `MEM_B(0XF50, ctx->r1) = 0;` is restored in `funcs_23.c:9788` before ending session.
5. Regen if this touches `RecompiledFuncs/*.c` content: `fixup_game_funcs.py` edit → clear
   `RecompiledFuncs/*.c` → `N64Recomp/build/N64Recomp rogue_squadron.toml` → `python3
   fixup_game_funcs.py` → `cmake --build build -j8`.

**Discriminating outcome**: if `initN64RspMixer`'s write interleaves with gate1's reads throughout the
log (not just once at the top), and its written value stays near 0, that's the reset mechanism —
confirmed. If it fires once (boot) or writes a large/nonzero value, it's ruled out and the next probe is
`funcs_32.c:29181` or a fresh grep for other `-0x68EC` references not yet found (the 8th write, if one
exists).

## Environment notes (carried forward, all still valid)

- Regen paths for game-code patches are in `/Users/williambuckley/Documents/Tools/N64Recomp`
  (`fixup_game_funcs.py`, `RecompiledFuncs/*.c`, `build/N64Recomp`, `rogue_squadron.toml`), NOT this
  repo (`~/Documents/Tools/RogueSquadron64Recomp`). This is a SEPARATE checkout from
  `lib/N64ModernRuntime`'s nested `N64Recomp` submodule — edits here do NOT need
  `submodule-patches/export.sh`. Only edits actually inside this repo's `lib/` need that.
- `cd` into `N64Recomp` FIRST as its own bare `cd` command, THEN run `./build/N64Recomp
  rogue_squadron.toml` with output redirection in a SEPARATE Bash call — combining `cd` and a redirect
  in one compound command triggers a permission prompt in this sandbox. Same for any cd+redirect combo.
- `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`
  clears RecompiledFuncs (use the ABSOLUTE path).
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from this repo's
  root — allowlisted verbatim, works as a single command.
- Soak driver template: `scratch/s73_post_a_scene/run_step317ratrace.sh` (now the newest; copy it, don't
  hand-roll — same breadcrumb set as the whole s310-317 lineage).
- Launch the soak via Bash with `run_in_background: true` (cd into `scratch/s73_post_a_scene` first as
  its own bare command), then `TaskOutput` with `block: true` and `timeout` up to 600000ms — do NOT
  foreground-poll. The soak's own 600s phase-timeout exits nonzero (exit 5, INCONCLUSIVE) on the
  expected deterministic hang — that's success for this soak design, not a tooling failure; the game
  process is killed automatically. Confirm `pgrep -f "build/RogueSquadron64Recomp"` is empty before AND
  after.
- `/tmp` is blocked for redirects — use a path inside this repo, `N64Recomp`, or `rogue_squadron64`
  instead.
- `ctx->r31` ($ra) is NOT a general-purpose "who called me" instrument in this recompiler's codegen —
  it's only meaningful right after code that explicitly assigns it (stack-restore, or an indirect-call
  trampoline computing a real return address). Direct `jal`s compile to plain C calls and never touch it.
  For "which call site fired" questions on direct-call functions, use exhaustive grep (as s317 did) or a
  distinct sentinel write at each site, not `ctx->r31` logging.
- `scratch/s73_post_a_scene/step317ratrace/run.log` (746 KB) is s317's saved log if a future session
  wants to re-verify the ra=0 finding before building anything new.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang (same slug, s303-317 — still the active
investigation thread. 11 of these sessions have each produced a discriminating result in sequence
(s303/s306/s307/s309/s310/s311/s312/s313/s315/s316/s317), resetting the iron-rule-8 no-progress counter
every time; s314 (maintenance) doesn't count. Continue the same slug next non-maintenance session.)
