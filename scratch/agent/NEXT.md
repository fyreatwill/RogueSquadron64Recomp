# NEXT work unit — M3: find what populates the MusyX DMA-batch array (s103)

s102 cleared both `submitDmaRequestBatch` and the `musyxSynthFrame` call
site as the bug site — the corrupted `devAddr` is already present in the
batch array (`a0=0x80179A60` this run) at the moment `musyxSynthFrame`
reads it, before the call. Read PORTING-STATE.md's Session 102 entry
before doing anything else; this file only has the actionable summary.

## What's confirmed (do not re-derive)

- `submitDmaRequestBatch` (`funcs_1.c:6168`, guest `0x8000569C`): `a0`
  = pointer to an array of 12-byte `{size, devAddr, dramAddr}` entries
  (offsets `+0x0/+0x4/+0x8`), `a1` = count, faithful copy loop into the
  DMA ring. No bug here.
- `musyxSynthFrame`'s call site (`funcs_24.c:3856-3875`): `a0 =
  MEM_W(G_BASE-0x68D8)` (a genuine pointer value), `a1 =
  MEM_HU(G_BASE-0x68DC)` (count/gate), `a2 = G_BASE-0x68D0` (a real
  address, unused in the copy loop). Registers correctly mapped. No bug
  here either.
- The batch array's `devAddr` field is corrupted **before** either
  function above ever touches it. All 9 entries in the s102 soak's
  batch decode as one of two consistent 4-byte shapes: `"lg"+<1
  varying byte>+"r"` or `"wi"+<1 varying byte>+"g"` — a structured
  tag/index-like value, not noise. `size`/`dramAddr` in the same
  entries are sane (dramAddr increments by the previous entry's size
  exactly).
- `entry=1`'s exact value (`devAddr=0x6C676672`, decodes `"lgfr"`) has
  now recurred byte-identical across s85/s91(x2)/s93/s94/s101/s102 — 7
  occurrences, always this exact bit pattern. Not a race, not a stomp,
  not run-to-run noise (all already refuted, do not reopen).
- `ROGUESQ_LOG_MUSYX_DMA_CALL=1` is a real, working instrument (fired
  17/17 in s102) — keep it armed in every future soak alongside the
  rest of the family set.

## The work unit

Find the function that writes the batch array at `a0` (this session:
`0x80179A60` — likely a fixed/reused buffer address across runs, worth
confirming with one more soak before assuming so) with the wrong
`devAddr` field, then read its source to find the field-mapping bug.

1. **Check whether `a0` is a fixed address first** (cheap, no
   rebuild): grep `RecompiledFuncs/funcs_24.c` and neighboring files for
   `0x80179A60` or `0x8017` lui/addiu pairs near `musyxSynthFrame` — if
   this buffer address is a compile-time constant (a static array, not
   a heap/stack pointer), that narrows the search enormously: grep all
   `funcs_*.c` for stores (`sw`/`MEM_W(...) =`) to that same base
   address or a register set to that lui/ori pair. This is the highest
   information-value first step — it may directly name the writer
   without needing a new instrument.
2. **If step 1 doesn't find it** (e.g. the pointer is computed/indexed,
   not a bare constant): re-read `G_BASE-0x68D8`'s neighborhood for
   what *writes* it (not what reads it, already done in s102) — grep
   for stores to `-0x68D8(...)` relative to `0x8015<<16` across
   `funcs_*.c`. Whatever writes that global pointer variable is called
   earlier in the same per-VI-retrace tick (probably still inside the
   MusyX audio subsystem, possibly a "start next sample" or "queue
   sample stream" function) — reading that function's body should reveal
   which of ITS source fields it copies into the array's `devAddr`
   slot, and hence which field is wrong (name/tag table entry instead
   of a ROM sample-data offset).
3. **Once the populating function is found**, read its body the same
   way s102 read `submitDmaRequestBatch` — confirm from the actual
   instructions which source field maps to the array's `devAddr`
   before writing any patch. Do not guess.
4. **If a wrong-field/wrong-offset bug is confirmed**: fix at the
   source (`N64Recomp/fixup_game_funcs.py`, guest-side hand patch),
   following the exact-instruction-anchor, file-scoped, "verify patched
   xN in only the expected file" discipline every prior guard/patch
   this arc has used (s99-102).
5. **If the mechanism is genuinely NOT a simple wrong-field read** (e.g.
   a legitimate variant-interpretation of the same bytes, or something
   that needs a MusyX format spec to understand) — characterize that
   precisely and write it up; a correct root-cause without a landed fix
   remains a valid outcome (same as s102).
6. Regen order if anything beyond `fixup_game_funcs.py` needs changing
   (unlikely): `make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` →
   `cmake --build`. If only editing `fixup_game_funcs.py`, re-running it
   alone is enough — **but see the tooling note below first.**
7. Rebuild: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j 8` — exit clean (only the pre-existing-class format/sign warnings).
8. Soak with the full flag set (same as s102's command, still in
   `scratch/s73_post_a_scene/run_mission_keys.sh`) plus whatever new
   flag this session adds. Run in the background; wait for the PID the
   wrapper script prints (or `pgrep -x RogueSquadron64Recomp`, never
   `pgrep -f "build/RogueSquadron64Recomp"` — s100's lesson, argv0 has
   no `build/` prefix) to exit before reading `run.log`.

## Tooling note — fix before it compounds further (optional but cheap)

`fixup_game_funcs.py` is **not idempotent**: every patch's regex anchor
matches text that's unchanged after insertion, so re-running the script
without a full ELF regen in between inserts a duplicate of every
already-applied patch. Confirmed s102: `funcs_40.c` has **3 copies** of
the s100 `composeNpcOrientationMatrix` guard (accumulated across
s100/s101/s102's re-runs). Harmless so far (duplicates are dead code —
first copy's `goto` always wins), but bloats the generated C every
session. If this session touches `fixup_game_funcs.py` again, consider
fixing it: make each anchor's regex also require the match is **not**
immediately followed by `{ // PATCH:` (a lookahead), so a second run is
a true no-op. Cheap, self-contained, does not require regenerating
anything to test — just run the script twice in a row and confirm the
2nd run reports "no changes needed" / 0 for every already-landed patch.

## Do not

- Do not re-soak `activateAnimationKeyframe`, `composeNpcOrientationMatrix`,
  or `projectModelBoundsToScreen` guards — all three landed and
  validated (s99-101), leave their `ROGUESQ_LOG_*_GUARD` flags armed but
  treat them as closed.
- Do not re-instrument `submitDmaRequestBatch` or the `musyxSynthFrame`
  call site itself — both are now cleared as the bug site (s102). Any
  new instrument goes further upstream, at whatever populates the array.
- Do not cite `ra=0x00000000` as corruption evidence (refuted s92,
  reconfirmed every session since).
- Do not re-open "random/race/stomp" framings for the `devAddr`
  corruption — s102 added a 3rd independent line of evidence against
  all three (structured 2-shape pattern across a whole batch, not just
  one value).
- Do not assume `musyxSynthFrame` is part of the "never-called" MusyX
  RSP audio ucode M5 describes — still unconfirmed either way.
- Do not compare a raw `ctx->rN` (`gpr`/`uint64_t`) value against 32-bit
  literal bounds in any new guard — always truncate through `U32()`
  first for comparisons; for pointer *arithmetic* (dereferencing),
  never truncate — keep the full sign-extended `gpr` value (s102 lesson
  from writing the `ROGUESQ_LOG_MUSYX_DMA_CALL` instrument: MEM_W's
  address math relies on the 0xFFFFFFFF80xxxxxx sign extension).
- Do not trust a `fixup_game_funcs.py` "patched xN" report without
  checking which file(s) it patched, **and consider whether it's a
  duplicate of an already-landed patch** (see tooling note above).
- `N64Recomp/fixup_game_funcs.py` is untracked in N64Recomp's own git,
  by design — do not attempt to commit it there; the durable record
  lives in `PORTING-STATE.md`/`CURRENT-TRUTH.md` in this repo.
