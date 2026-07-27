# NEXT work unit — audit the regen pipeline for patch duplication FIRST, then re-soak the corrected voice-active-gate instrument (s121)

s120 found a serious regen-pipeline reliability bug partway through the M3
voice-corruption investigation and spent the rest of the session on it. Read
PORTING-STATE.md's Session 120 entry before doing anything else; this file
only has the actionable summary.

## Step 1 (do this first, it's cheap and blocks trusting anything else)

`N64Recomp`'s regen does not reliably produce a clean, single-copy-of-every-
patch build, even when every `RecompiledFuncs/funcs_*.c` file is deleted
before regenerating. Confirmed twice this session: a from-scratch
delete-all → `N64Recomp` → `fixup_game_funcs.py` → `cmake` cycle produced a
compile-blocking duplicate label (`funcs_3.c`'s `L_dlentry_guard_exit`) the
first time, and a **different** pair of files (`funcs_3.c` again plus
`funcs_40.c`'s `L_hangarbay_guard_exit`) the second time, with `funcs_23.c`/
`funcs_24.c`'s non-label diagnostic patches also silently doubled both times
(harmless to behavior, just double-logging). Root cause not found — ruled out
cmake auto-invoking fixup, ruled out `glob()` duplicate enumeration.

Before running any new soak:
1. Run the full clean regen once (see "Regen reminder" below).
2. For every patch in `fixup_game_funcs.py`, grep its unique static-variable
   name (or label name) across all 45 `RecompiledFuncs/funcs_*.c` files and
   confirm the count matches expectations (1 copy per intended site, or the
   patch's own documented multiplicity — e.g. `s_hangarbay_guard_enabled`
   should be 5 sites × 1 copy = 5, not 10). A one-time script that lists
   every `static int s_..._enabled` / `static int s_..._n` / `^L_..._exit:`
   declaration and its count per file would catch this mechanically instead
   of one compile-error at a time.
3. If anything is doubled: for label conflicts, hand-fix by deleting the
   second copy (as s120 did) — this is a generated-file fix, not durable,
   and will need repeating if the underlying bug isn't found. For non-label
   duplicates, decide whether to leave them (harmless) or hand-fix for
   hygiene before soaking.
4. Only after the report is confirmed clean, proceed to Step 2.

This is worth a dedicated future investigation on its own (why does
`N64Recomp` sometimes restore already-patched content even after the output
file is deleted?) but is NOT this session's primary target — treat it as a
gate to clear, not the work unit itself, unless it resists a quick fix.

## Step 2: re-soak the corrected voice-active-gate instrument

s120 added `count=`/`arrayBase=` fields to `ROGUESQ_LOG_VOICE_ACTIVE_GATE=1`'s
`[voice-active-gate-nz]` log, reading `-0x6900` (loop bound) and `-0x6908`
(array base) directly at the exact corruption instant — the discriminating
data needed to explain s120's core finding: in 2/2 soaks, every corrupted
scan index `idx` **exceeded the currently-live allocation's own `voiceCount`**
(burst 1: idx 16-17 vs `voiceCount=15`; burst 2: idx 19-31 vs `voiceCount=18`),
while the base address arithmetic (`base − idx*0x88`) proved the scan was
reading the *current, valid* allocation, not a stale one. The first attempt
at this exact instrument had a bug (bare 32-bit literal instead of the
codebase's `S32(...)`-then-assign-to-`gpr` sign-extension idiom), producing
nonsense (`count=0x0029 arrayBase=0x72657375`) — this was caught and fixed in
the same session (see `fixup_game_funcs.py`'s `_voice_active_gate_patch`,
`s_vagn_base_reg` intermediate) but **never actually soak-tested** because
the pipeline bug above ate the remaining session time.

Run (after Step 1's audit is clean):
```
env ROGUESQ_LOG_SONG_ARRAY_LIFECYCLE=1 ROGUESQ_LOG_VOICE_ACTIVE_GATE=1 \
  PROBE_MODE=start_only HOLD_S=30 zsh \
  scratch/s73_post_a_scene/run_mission_keys.sh songlifecycle3 5 8
```
Then `grep "voice-active-gate-nz\] n=" scratch/s73_post_a_scene/songlifecycle3/run.log`
and check the `count=`/`arrayBase=` fields:
- If `count=` matches the currently-live allocation's real `voiceCount`
  (e.g. 15 or 18, not some other value) and `arrayBase=` matches the real
  pointer (e.g. `0x801714D0`): the loop bound read is sane and the mystery
  shifts to "why does a sane `idx < count` check let idx reach values ≥
  count" — re-check the actual comparison instruction (`funcs_24.c` around
  0x80090F44-0x80090F54) for a sign/width bug (e.g. `idx` and `count` both
  `& 0xFFFF`-masked — check for a wraparound if idx or count is ever
  negative-looking before the mask).
- If `count=`/`arrayBase=` are themselves garbage (not matching any known
  allocation): that's the real discriminating result — the globals
  themselves are being corrupted independent of the heap-array-content
  corruption s118 characterized, pointing to a write hitting the BSS/global
  data segment (`~0x801496F8-0x80149700`), a different memory class than
  the heap array itself. This would be a major reframing (two-region
  corruption, not one) and should go straight into CURRENT-TRUTH with the
  exact addresses.

Per rule 8: this soak (whichever the 3rd `songlifecycle*` run) is allowed;
if it's non-discriminating, park this specific sub-question and pivot to
either the s120-identified alias bug's own eventual fix (worth doing
regardless of causality here) or a fresh source-read of the exact
idx-vs-count comparison instructions.

## Do not

- Do not re-test the `shutdownAudioEngine`/`-0x6904` alias hypothesis as the
  cause of the observed corruption — directly refuted 2/2 (`[shutdown-audio-
  free]` fired 0 times in both soaks). The bug itself is still real and
  worth fixing someday (asymmetric free of two aliased globals), just not
  causal here.
- Do not re-litigate hypothesis (b) from s117-119 (`musyxInitVoiceFromSample`
  comparison) — closed, see PORTING-STATE s119.
- Do not write any new `MEM_W`/`MEM_HU`/`MEM_BU` call with a bare hex literal
  for the "offset"/"reg" argument that represents a `lui`-computed base.
  Always go through `(gpr)(int32_t)(0Xnnnn << 16)` (or reuse an in-scope
  `ctx->rN` that already holds a correctly sign-extended value) — a bare
  `0x80150000`-style literal types as `unsigned int` in C, which zero-
  extends instead of sign-extends in the macro's 64-bit arithmetic and
  silently computes the wrong address. This bug cost most of s120's late
  session; the fixed idiom is in `_voice_active_gate_patch` now as a
  template to copy.

## Regen reminder (UPDATED mechanics — delete-first is now mandatory)

1. Delete all existing output first (do NOT skip this):
   ```
   python3 -c "
   from pathlib import Path
   import os
   base = Path('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs')
   for f in base.glob('funcs_*.c'): os.remove(f)
   "
   ```
2. `python3 <rogue_squadron64>/tools/make_elf.py` (absolute path, no `cd`)
3. `zsh tools/agent/regen_n64recomp.sh` (new this session — wraps
   `cd .../N64Recomp && ./build/N64Recomp rogue_squadron.toml` as a single
   allowlisted command, works around the headless permission-prefix wall
   rule 10 describes for `cd X && Y`-style compound commands)
4. `python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   — **read the full report, not just grep for your own patch** — confirm
   every line's `x{n}` matches its expected/intentional multiplicity.
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8`
   — grep for `error:` explicitly; a clean exit does not guarantee no
   duplicate-but-non-erroring patches (see Step 1 above).
6. Soak via `env <FLAGS> PROBE_MODE=start_only HOLD_S=30 zsh
   scratch/s73_post_a_scene/run_mission_keys.sh <tag> 5 8`.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is over the ~35 KB target (now larger after s120's
additions). Migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md and prune superseded detail, paired with a real
experiment — not on its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-120
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`, including
s120's hand-edits to `funcs_3.c`/`funcs_40.c` to remove duplicate labels —
these hand-edits will be LOST on the next full regen unless the underlying
duplication bug is fixed first). Same posture as the `rogue_squadron64`
sibling checkout flagged since s54. Worth asking the user whether/how to
commit that history.
