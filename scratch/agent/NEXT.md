# NEXT work unit — M3: find the allocator for fillSampleStreamRange's range-list nodes (s104)

s103 refuted its own leading hypothesis (`acquireSampleStreamBlock`
copies a cache-key argument verbatim into the DMA batch's `devAddr`) and
found the *real* entry-writer instead: `fillSampleStreamRange`. Read
PORTING-STATE.md's Session 103 entry before doing anything else; this
file only has the actionable summary.

## What's confirmed (do not re-derive)

- `G_BASE-0x68D8` (the DMA batch array's base-pointer global) is written
  **once**, at MusyX init (`setupSongRenderBuffers`, `funcs_23.c:11344`,
  a one-time `rs_malloc`). Not a per-tick writer — the array's contents,
  not its base pointer, are what's corrupted each tick. Do not re-chase
  this global as a lead.
- `acquireSampleStreamBlock` (`funcs_23.c:11871`, guest `0x8008F758`) —
  source-read in full. It manages a cache of "sample stream blocks"
  keyed by its `a0` argument, via a linked list rooted at global
  `-0x6650` (active) / `-0x6654` (free pool). On a cache miss it **does**
  append a DMA batch entry (`entry.devAddr = a0` verbatim, `entry.size =
  0x100`, `entry.dramAddr = node->0x8`) — this code is real and was a
  strong-looking suspect. **Ruled out for this run specifically**: the
  `ROGUESQ_LOG_STREAM_TAG=1` instrument (logs `a0` at function entry, the
  earliest possible point) fired **0/0** in s103's soak despite the
  batch's count field (`G_BASE-0x68DC`) proving 9 entries were appended
  the same tick — so this function was not entered at all this run. Its
  own code may still be buggy in principle (verbatim tag-copy, no
  translation) but it is **not this bug**, at least not exclusively —
  do not spend another soak re-testing this specific function unless new
  evidence points back to it.
- `fillSampleStreamRange` (`funcs_23.c:12473-12630`, guest `0x8008FAAC`)
  is the **actual writer** for this run's crashing batch, confirmed by
  program order (called from `musyxRenderVoiceSamples`,
  `funcs_24.c:452/524`, *before* `acquireSampleStreamBlock` at line 536)
  and by matching guest addresses. Its entry-append code (guest
  `0x8008FB40-0x8008FB90`) computes:
  - `entry.devAddr = node->0x8 + node->0x10`
  - `entry.size` = a locally-computed fill-gap byte count (rounded to
    256-byte boundary from range-overlap math earlier in the function)
  - `entry.dramAddr = node->0x14 + node->0x10`
  All three are sums of struct fields / computed values, not a raw
  argument copy — the opposite shape from the refuted hypothesis. `node`
  here (register `$t0`) comes from walking a **different** linked list,
  rooted at global `-0x664C` — NOT the same list `acquireSampleStreamBlock`
  manages (`-0x6650`/`-0x6654`). Two distinct cache systems, don't
  conflate them.
- `acquireSampleStreamBlock`'s node-init path (labels `L_8008F7A4`
  through `L_8008F800`, the "new block" / cache-miss branch) was fully
  read and **does not touch offsets `0x8`, `0x10`, or `0x14`** of the
  node it creates — only `0x0` (list-link, zeroed), `0x4` (zeroed),
  `0xC` (tag), and `0x10` is reused as a *different* field (a status
  enum "2") in that function than what `fillSampleStreamRange` reads
  from `0x10` on its own `-0x664C`-list nodes (a byte-length/fill-progress
  counter it compares against a `0x600` constant) — this is expected,
  since they're different node types on different lists, not evidence
  of an offset-mapping bug by itself.
- A `664C` grep across **all** `funcs_*.c` (not just `funcs_23.c`) found
  every other hit is an unrelated absolute-address substring collision
  (e.g. `0x800B664C`, a totally different guest address that happens to
  contain "664C") — the real `-0x664C` global (relative to `0x8015<<16`)
  is referenced **only** within `funcs_23.c`. Whatever allocates/
  initializes `fillSampleStreamRange`'s range-list nodes must also live
  in that file.
- `ROGUESQ_LOG_MUSYX_DMA_CALL=1` and `ROGUESQ_LOG_STREAM_TAG=1` are both
  real, working instruments — keep both armed in every future soak.
  `do_rom_read` recurred an 8th time this session, byte-identical to
  every prior occurrence (`phys=0x1C676672`-family, same ~140s/hold+11s
  window). Not itself informative anymore beyond "still deterministic,
  still reachable" — don't spend a work unit re-confirming it again
  unless something about the shape changes.

## The work unit

Find the function that **allocates and initializes** the `-0x664C`
linked-list nodes `fillSampleStreamRange` reads from — specifically,
whatever sets a new node's `+0x8` field (the value that becomes
`devAddr`'s base) at creation time. That initializer is the next
candidate for the actual field-mapping bug: if `+0x8` gets set from a
tag/name value instead of a real ROM address, `fillSampleStreamRange`'s
otherwise-correct arithmetic (`node->0x8 + node->0x10`) would faithfully
propagate the corruption forward — matching s102's observation that
`devAddr` is wrong while `size`/`dramAddr` are sane.

1. **Grep `funcs_23.c` for other stores to a `-0x664C`-relative global**
   or for code that inserts a NEW node into that list (mirroring the
   `L_8008FBB8`-`L_8008FBF8` region already read in
   `fillSampleStreamRange` itself, which does list *maintenance*
   (unlink/relink) but appears to operate on **existing** nodes found
   via the loop at `L_8008FADC`, not create new ones — if no allocator
   is found in `fillSampleStreamRange` itself, it must be a separate
   function called from elsewhere, most likely still inside
   `musyxRenderVoiceSamples` or a sibling MusyX setup function in
   `funcs_23.c`/`funcs_24.c`). Read `musyxRenderVoiceSamples`
   (`funcs_24.c`, starts around line 6, the enclosing function for the
   two `fillSampleStreamRange` calls at 452/524) in full if the
   allocator isn't obvious from a grep — it likely calls something
   *before* `fillSampleStreamRange` to ensure a range node exists for
   the current stream, which is where `+0x8` would first get set.
2. **Once found, read its body** the same disciplined way s102/s103 did
   for their targets — confirm from the actual instructions which
   source field maps to the new node's `+0x8`, before writing any patch
   or drawing a conclusion. Do not guess.
3. **If a wrong-field/wrong-offset bug is confirmed**: fix at the source
   (`N64Recomp/fixup_game_funcs.py`, guest-side hand patch), following
   the exact-instruction-anchor, file-scoped, "verify patched xN in only
   the expected file" discipline every prior guard/patch in this arc has
   used (s99-103).
4. **If the mechanism is genuinely NOT a simple wrong-field read**
   (e.g. `+0x8` is set correctly and the corruption is even further
   upstream, or turns out to be a legitimate value under some
   MusyX-format interpretation this repo doesn't have docs for) —
   characterize precisely and write it up; a correct root-cause without
   a landed fix remains a valid outcome (same as s102/s103).
5. **Regen order** if `fixup_game_funcs.py` changes:
   `python3 /Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py`
   → N64Recomp (see command below) → `fixup_game_funcs.py` →
   `cmake --build`. **Do a full regen from ELF, not a bare
   `fixup_game_funcs.py` re-run**, unless you've first applied the
   idempotency fix described below — otherwise every already-landed
   patch duplicates again (s102's finding, worked around but not fixed
   in s103).
   - N64Recomp step: direct `Bash` invocation of `./build/N64Recomp` or
     `cd &&` chains may get denied by the sandbox (hit this in s103) —
     use `python3 -c "import subprocess; subprocess.run([...],
     cwd='/Users/williambuckley/Documents/Tools/N64Recomp', ...)"`
     instead, which is not denied (matches the older note this repo's
     docs already had about `subprocess.run(cwd=...)` working when
     direct `Bash cd &&` chains don't).
6. Rebuild: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j 8` — exit clean (only the pre-existing-class format/sign warnings).
7. Soak with the full flag set (same as s102/s103's command, in
   `scratch/s73_post_a_scene/run_mission_keys.sh`) plus whatever new
   flag this session adds:
   `env ROGUESQ_LOG_MUSYX_DMA_CALL=1 ROGUESQ_LOG_STREAM_TAG=1 <new flag>=1 ROGUESQ_LOG_THREAD_RESUME=0 PROBE_MODE=start_only HOLD_S=30 zsh run_mission_keys.sh <tag> 30 12`
   (background it; wait for the run to finish rather than polling —
   `pgrep -x RogueSquadron64Recomp` to check liveness, never
   `pgrep -f "build/RogueSquadron64Recomp"` — s100's lesson, argv0 has
   no `build/` prefix).

## Tooling note — still not fixed, still cheap

`fixup_game_funcs.py` is **not idempotent** (flagged s102, worked around
but not fixed s103 by doing a full regen instead). If this session
touches `fixup_game_funcs.py` again, consider actually fixing it this
time: make each patch's anchor regex also require a negative lookahead
that the match is **not** immediately followed by `    { // PATCH:` (the
literal string every diagnostic/guard patch inserts right after its
anchor — confirmed by grepping the script's own `PATCH:` occurrences).
Test by running the script twice in a row on an already-regenerated
tree and confirming the 2nd run reports 0/"no changes needed" for every
already-landed patch.

## Do not

- Do not re-soak specifically to re-test `acquireSampleStreamBlock` —
  refuted this session (0/0 despite proof-of-9-entries-appended). Its
  own verbatim-tag-copy code may still independently be worth fixing
  someday (defense in depth), but it is not this run's bug.
- Do not re-instrument `musyxSynthFrame`, `submitDmaRequestBatch`, or
  `setupSongRenderBuffers` — all cleared (s102/s103). Any new instrument
  goes to the `-0x664C` list's allocator/initializer specifically.
- Do not conflate `acquireSampleStreamBlock`'s block-cache list
  (`-0x6650`/`-0x6654`) with `fillSampleStreamRange`'s range-cache list
  (`-0x664C`) — confirmed distinct lists, distinct node layouts (field
  `+0x10` means different things on each).
- Do not cite `ra=0x00000000` as corruption evidence (refuted s92,
  reconfirmed every session since).
- Do not re-open "random/race/stomp" framings for the `devAddr`
  corruption — s102/s103 together add a 4th and 5th independent line of
  evidence against all three (structured pattern, deterministic byte-
  identical recurrence across 8 sessions now, and a fully-traced
  computed-arithmetic write site whose inputs must therefore be what's
  wrong, not the write itself).
- Do not assume `musyxSynthFrame`/`musyxRenderVoiceSamples` are part of
  the "never-called" MusyX RSP audio ucode M5 describes — still
  unconfirmed either way, and s101/s103 show this code path clearly
  does run (both instruments fire) — leaning against M5's framing but
  not yet conclusive.
- Do not compare a raw `ctx->rN` (`gpr`/`uint64_t`) value against 32-bit
  literal bounds in any new guard — always truncate through `U32()`
  first for comparisons; for pointer *arithmetic* (dereferencing), never
  truncate — keep the full sign-extended `gpr` value.
- Do not trust a `fixup_game_funcs.py` "patched xN" report without
  checking which file(s) it patched, **and do a full ELF regen first**
  if the tree may already carry prior patches (see tooling note).
- `N64Recomp/fixup_game_funcs.py` is untracked in N64Recomp's own git,
  by design — do not attempt to commit it there; the durable record
  lives in `PORTING-STATE.md`/`CURRENT-TRUTH.md` in this repo.
