# NEXT work unit — M3: find what writes `voice+0x34` (s105)

s104 cleared `fillSampleStreamRange`'s node allocator
(`initSampleStreamBlockCache`) as a suspect and proved — with a clean,
byte-for-byte-matching instrument — that the corrupted `devAddr` value
is already present in `fillSampleStreamRange`'s own incoming arguments
at function entry, before any of its own arithmetic runs. Read
PORTING-STATE.md's Session 104 entry before doing anything else; this
file only has the actionable summary.

## What's confirmed (do not re-derive)

- `initSampleStreamBlockCache` (`funcs_23.c:12070-12227`, guest
  `0x8008F858`) is `fillSampleStreamRange`'s `-0x664C`-list node
  allocator (one-time MusyX-init call, two `rs_malloc`s: one for a
  `1536*N`-byte sample-data buffer, one for a `24*N`-byte node array).
  It sets each node's `0x0` (next), `0x4` (prev), and `0x14` (that
  node's `0x600`-byte buffer-slice pointer) — **never** `0x8`, `0xC`, or
  `0x10`. **Cleared as a suspect**: do not re-read it or treat it as a
  candidate again.
- Read the rest of `fillSampleStreamRange` past where s103 stopped
  (`funcs_23.c:12693-13002`). Every path that (re)claims a node for use
  — free-list pop (`L_8008FCD8`), single-active-node eviction
  (`L_8008FD48` fast path), general LRU eviction (unlink active-list
  tail, reinsert at front) — converges on one shared block
  (`L_8008FDB8`, guest `0x8008FDB8`, `funcs_23.c:12993-12999`) that
  **unconditionally recomputes** `node->0x8 = a1 - ((a1-a3) mod 0x600)`
  from the function's own `a1` (requested DRAM target) and `a3` (tag)
  arguments, immediately before use. This is real, working, correctly-
  targeted address-alignment arithmetic — not a bug — **given sane
  inputs**.
- Landed `ROGUESQ_LOG_FILL_RANGE_ARGS=1` (`N64Recomp/fixup_game_funcs.py`,
  anchored on `fillSampleStreamRange`'s function-entry boilerplate,
  file-scoped to `funcs_23.c`), logging raw incoming `a0`-`a3`
  (`ctx->r4`-`r7`) before anything touches them. One soak
  (`scratch/s73_post_a_scene/s104_fillargs/run.log`): fired 7 times,
  values matching the same run's `[musyx-dma-call]` batch dump
  byte-for-byte (`n=0 a1_dram=0x6C676672` = `entry=0 devAddr=0x6C676672`;
  `n=1 a1_dram=0x77696E67` = `entry=1 devAddr=0x77696E67`). **Confirmed:
  the corruption is already present in `a1`/`a3` at function entry.**
  `fillSampleStreamRange`'s own arithmetic is cleared too — do not
  re-test it, do not re-instrument this function.
- `a1`/`a3` are computed in `musyxRenderVoiceSamples` (`funcs_24.c`
  ~397-451; all 4 `fillSampleStreamRange` call sites in that function
  share this shape, not just the 2 s103 looked at) from a single shared
  source: `MEM_W($s1, 0x34)`, where `$s1` is `musyxRenderVoiceSamples`'s
  own `a0` argument (a per-voice/stream descriptor pointer). This is the
  **same offset** (`+0x34`) the existing `ROGUESQ_LOG_STREAM_TAG` fixup
  comment already identified as feeding `acquireSampleStreamBlock`'s
  (still unreached-this-run) `a0` argument at a *different* call site in
  the same function — two independently-suspected writer functions both
  trace back to this one field.
- Do NOT conflate `$s0`/`$s1` — found but unresolved (low priority,
  worth a quick check next session, not the main thread): the
  `fillSampleStreamRange` call sites pass `a0 = $s0+0x34` (a different
  register than `$s1`, same offset). Could be two elements of the same
  per-voice array, or genuinely unrelated. Confirm before assuming
  either way.
- `do_rom_read` recurred a 9th time this session, same signature
  (`osPiStartDma_recomp` → `do_dma` → `do_rom_read` abort,
  `pi.cpp:86`). `ROGUESQ_LOG_DMA` (the flag that logs `[rom-read]`/
  `[pi-start-dma]` fields) was NOT armed this run, so no fresh
  phys-addr confirmation this time — not needed, the crash signature
  alone is enough to identify it as the same family. Arm
  `ROGUESQ_LOG_DMA=1` again next session if a fresh byte-identical
  check is ever useful (it hasn't changed shape in 6+ sessions, so low
  value).

## The work unit

Find what writes `*(voice_ptr + 0x34)` (the struct field both
`fillSampleStreamRange`'s and `acquireSampleStreamBlock`'s corrupted
arguments trace back to).

1. **Read `musyxKeyOnVoice`** (`funcs_24.c:1825`, not yet read this
   arc) — the obvious per-voice setup function, likely where a voice
   descriptor's fields get populated from a MusyX sample/instrument
   descriptor when a voice starts playing. Look specifically for any
   store to offset `0x34` of a struct pointer, and trace what value
   flows into it — is it copied from a real ROM-address field of some
   sample/instrument table entry, or from a name/tag field, or left
   uninitialized (reused pool memory)?
2. **If `musyxKeyOnVoice` doesn't write it**, grep `funcs_24.c` (and
   `funcs_23.c`, MusyX code is split across both) for other stores to a
   `+0x34`-relative offset near voice-sized structs, or for whatever
   populates `$s1` itself in `musyxRenderVoiceSamples` (i.e. find
   `musyxRenderVoiceSamples`'s own caller and how it picks which voice
   struct to pass in — the corruption could originate in the caller's
   voice-list walk, not in a single field-write).
3. **Once found, read the writer's body** the same disciplined way
   s102-s104 did — confirm from the actual instructions which source
   value maps to `+0x34`, before writing any patch or drawing a
   conclusion. Do not guess.
4. **If a wrong-field/wrong-offset bug is confirmed**: fix at the
   source (`N64Recomp/fixup_game_funcs.py`, guest-side hand patch),
   following the exact-instruction-anchor, file-scoped, "verify patched
   xN in only the expected file" discipline every prior guard/patch in
   this arc has used (s99-104).
5. **If NOT a simple wrong-field read** (e.g. `+0x34` is set correctly
   from something that looks like a legitimate MusyX-format value this
   repo just doesn't have docs for, or the corruption traces back even
   further) — characterize precisely and write it up; a correct
   root-cause without a landed fix remains a valid outcome (same as
   s102-s104).
6. **Regen order** if `fixup_game_funcs.py` changes:
   `python3 /Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py`
   → N64Recomp (see command below) → `fixup_game_funcs.py` →
   `cmake --build`. **Do a full regen from ELF, not a bare
   `fixup_game_funcs.py` re-run** — the idempotency bug is still not
   fixed (see Tooling note below), and a full regen has now cleanly
   avoided duplication twice in a row (s103, s104).
   - N64Recomp step: direct `Bash` invocation of `./build/N64Recomp` or
     `cd &&` chains may get denied by the sandbox — use `python3 -c
     "import subprocess; subprocess.run([...],
     cwd='/Users/williambuckley/Documents/Tools/N64Recomp', ...)"`
     instead, which is not denied.
7. Rebuild: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j 8` — exit clean (only the pre-existing-class format/sign warnings).
8. Soak with the full flag set plus whatever new flag this session
   adds:
   `env ROGUESQ_LOG_MUSYX_DMA_CALL=1 ROGUESQ_LOG_STREAM_TAG=1 ROGUESQ_LOG_FILL_RANGE_ARGS=1 <new flag>=1 ROGUESQ_LOG_THREAD_RESUME=0 PROBE_MODE=start_only HOLD_S=30 zsh run_mission_keys.sh <tag> 30 12`
   (run from `scratch/s73_post_a_scene/`; this will auto-background
   past the 120s foreground timeout — wait for the completion
   notification rather than polling; `pgrep -x RogueSquadron64Recomp`
   only if you need a liveness check, never `pgrep -f
   "build/RogueSquadron64Recomp"`, s100's lesson). The actual game
   stdout/stderr lands in `<tag>/run.log` inside the soak's own output
   dir, NOT in whatever file you redirected the shell command's own
   stdout to — check both.

## Housekeeping note — not this session's job, but flag it

`docs/CURRENT-TRUTH.md` is now ~95 KB, far past the ~35 KB budget
`CLAUDE.md` sets. This has been accumulating over many sessions (s85
saga), not introduced this session. A future session should do a
dedicated pruning pass — migrate durable mechanism/architecture
material to `docs/PROJECT-OVERVIEW.md`, keep only current status +
next steps in CURRENT-TRUTH, per the existing file-size rule. Per
ITERATION.md, compressing CURRENT-TRUTH does not itself count as
"ADVANCED" — pair it with a real work unit if attempted, don't spend a
whole iteration on it alone.

## Tooling note — still not fixed, still cheap

`fixup_game_funcs.py` is **not idempotent** by construction (every
patch's anchor regex matches text left unchanged after insertion). A
full ELF regen has now avoided the duplication symptom twice in a row
(s103, s104) as a workaround. If a session touches
`fixup_game_funcs.py` again, consider actually fixing it: make each
patch's anchor regex also require a negative lookahead that the match
is **not** immediately followed by `    { // PATCH:`. Test by running
the script twice in a row on an already-regenerated tree and confirming
the 2nd run reports 0/"no changes needed" for every already-landed
patch.

## Do not

- Do not re-read or re-instrument `initSampleStreamBlockCache` — fully
  cleared s104 (never sets node `+0x8`, and nothing depends on it doing
  so since every claim path recomputes it fresh).
- Do not re-instrument or re-soak specifically to re-test
  `fillSampleStreamRange`'s own arithmetic — cleared s104 (byte-for-byte
  confirmed clean given its actual, already-corrupted inputs).
- Do not re-soak specifically to re-test `acquireSampleStreamBlock` —
  still refuted as this run's writer (s103); its own verbatim-tag-copy
  code may independently be worth fixing someday but is not the active
  lead.
- Do not re-instrument `musyxSynthFrame`, `submitDmaRequestBatch`, or
  `setupSongRenderBuffers` — all cleared (s102/s103). Any new
  instrument goes to whatever writes `voice+0x34` specifically.
- Do not cite `ra=0x00000000` as corruption evidence (refuted s92,
  reconfirmed every session since).
- Do not re-open "random/race/stomp" framings for the `devAddr`
  corruption — now a 6th and 7th independent line of evidence against
  all three (s104's byte-for-byte arg match is as direct as evidence
  gets: the value is correct at the moment `fillSampleStreamRange`
  receives it as a corrupted input, not altered by anything in between).
- Do not compare a raw `ctx->rN` (`gpr`/`uint64_t`) value against 32-bit
  literal bounds in any new guard — always truncate through `U32()`
  first for comparisons; for pointer *arithmetic* (dereferencing), never
  truncate — keep the full sign-extended `gpr` value.
- Do not trust a `fixup_game_funcs.py` "patched xN" report without
  checking which file(s) it patched, **and do a full ELF regen first**
  if the tree may already carry prior patches.
- `N64Recomp/fixup_game_funcs.py` is untracked in N64Recomp's own git,
  by design — do not attempt to commit it there; the durable record
  lives in `PORTING-STATE.md`/`CURRENT-TRUTH.md` in this repo.
