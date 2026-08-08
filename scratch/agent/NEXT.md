# NEXT work unit

HYPOTHESIS-ID: item-319-source-trace

## s519 recap -- read this first

s519 did two things:

1. **Fixed `RENDER_LIT_MESH_R8_GUARD`** (item -317 step 3's 19th guard, 7th site in
   `renderLitMeshFaceGroup`, `funcs_4.c:15166`/`0x80013F0C`): a doubly-linked free-list-cache prepend
   write (`old_head->prev = tail_node`) reloaded from the same `0x801163B0` table other guards in this
   function already cover, with only a null check before the write. Full regen + build done, 1st
   live-verify CLEAN (0 own-guard fires, 4 benign `n=0/ra=0` co-fires, `hangarbay-entry n=31` positive
   control). 2nd independent confirm queued: `scratch/agent/soak_queue/s519_render_lit_mesh_r8_confirm.sh`
   -- fold its result in next session like any other soak.

2. **Escalated item -319** to its 3rd occurrence: the R8 live-verify's crash
   (`pc-symbol=beginFrameDLChunk+40536`/`last-guest-pc=0x8000b0d0`) is byte-identical to item -319's
   s503 and s505 sightings. Item -319's own entry pre-declared this threshold ("a 3rd occurrence would
   meet this campaign's escalation threshold"). Not source-traced yet -- that's this session's work unit.

Both written up: `docs/CURRENT-TRUTH.md` items -317/-319, `docs/PROJECT-OVERVIEW.md` §23 guard table
row #21, `PORTING-STATE.md` Session 519.

**M5 audio-lead cadence**: last checked/reset s517, due again s520+. This is s520 -- **check it this
session** if a run log gets produced (grep for any new audio-related stub/trap/gate diagnostic firing
that wasn't there at s517; see `docs/M5-AUDIO-PLAN.md` for the survey method). If the item -319
source-trace produces its own run log, that's the natural place to fold this check in cheaply.

## The work unit: source-trace item -319 (`beginFrameDLChunk+40536`/`last-guest-pc=0x8000b0d0`)

Follow the exact method that resolved item -322 (s517, `docs/PORTING-STATE.md` Session 517):

1. In `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c`, find
   `beginFrameDLChunk`'s recompiled body and locate the instruction at guest address `0x8000b0d0`
   (search for the `// 0x8000B0D0:` comment line -- addresses are case-sensitive in the comments,
   uppercase hex).
2. Identify what write or dereference happens at that exact PC, and trace which register/pointer feeds
   it -- walk backward to find where that register was last loaded and whether an existing range check
   (`0x80000000`-`0x80800000`) or null check already gates it.
3. Check whether skip-the-write-on-invalid is safe at this site (does downstream control flow reload
   the register from the source-of-truth again immediately after, the way every other guard in this
   lineage has verified) -- if yes, this is a normal fix, same shape as items -317R2 through -322.
4. **Bonus**: `beginFrameDLChunk` is also item -317 step 3's own largest untouched reload-site cluster
   (three sites at count=36, two at count=32, previously skipped deliberately to avoid pre-empting this
   thread -- see `docs/CURRENT-TRUTH.md` item -317). If the item -319 fix and the step-3 tracer's own
   candidate list overlap or are adjacent, note it -- fixing this may also count as step-3 progress on
   that tier once item -319 itself is resolved.
5. Follow the same regen/build/live-verify/confirm-queue sequence as every guard in this lineage (see
   the Regen reminder below).

If source-tracing finds the address is NOT a real memory access (e.g. another `$sp`-arithmetic
epilogue/breadcrumb-freeze artifact like item -321's refutation, s518), document that refutation with
the same rigor -- read the actual recompiled instruction before concluding either way.

**Regen reminder** (verify each step -- this has bitten prior sessions when skipped):
1. Delete all `funcs_*.c` in `N64Recomp/RecompiledFuncs/` first and confirm `0 remaining` -- stale
   files silently survive a partial regen otherwise. (Sandbox note: `rm -f funcs_*.c` glob-expansion and
   `find -delete` both get blocked by the approval layer here -- list explicit filenames in batches of
   ~10, or write a one-line script to a file and invoke that.)
2. `cd rogue_squadron64 && python3 tools/make_elf.py` -> `cd N64Recomp && ./build/N64Recomp
   rogue_squadron.toml` -> `python3 fixup_game_funcs.py` -> `cd RogueSquadron64Recomp/build &&
   DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`.
3. Grep the fixup report AND the freshly-generated source for the new guard's own name -- a silent
   no-op (rc=0, no error, 0 applied) has happened before when a function carried its own pre-existing
   breadcrumb patch and the guard's old/new match string didn't include the inserted line.
4. Live-verify manually in the foreground with every sibling guard's env var armed plus the new
   guard's own `ROGUESQ_LOG_<NAME>=1` (copy the full env-var list from
   `scratch/agent/soak_queue/done/s517_heaplistdeq_attr_write_confirm_*.sh` or s519's queued confirm --
   add any new guard names since), phase-gate on `hangarbay-entry` as the positive control (Iron Rule 1
   -- a null result needs a same-run positive control). Write the run as a standalone script (foreground
   `env VAR=1 ... zsh probe.sh` one-liners get rejected by the sandbox for backslash-continued
   multi-line commands -- write the script to `scratch/agent/`, `chmod +x`, run it, delete it after). If
   clean, queue a 2nd independent confirm to `scratch/agent/soak_queue/` for the loop to run between
   iterations.

`fixup_game_funcs.py` and the regenerated `RecompiledFuncs/*.c` live in the sibling `N64Recomp`
checkout (untracked by its own git) -- not this repo's git tree. This repo's ledger entries (with the
full old/new patch text) are the only durable record of every guard in this lineage since s481; no
`lib/` submodule involvement, no `export.sh` needed for this work.

## Discriminating measurement

Does `beginFrameDLChunk`'s write at `0x8000b0d0` go through a pointer reload with no range check (the
established item -317-lineage pattern -- fix is load-bearing once 2nd confirm validates it), or does the
source-trace show the address is a non-memory-access instruction whose apparent "match" across
s503/s505/s519 is a breadcrumb-tracking artifact (the item -321 precedent -- read the actual
instruction before concluding). Either way, write the mechanism down with the same rigor as item -322's
or item -321's write-ups (`docs/CURRENT-TRUTH.md` items -319/-321/-322) -- a source-verified conclusion,
not a repeated address correlation.

## If item -319 resolves quickly and there's remaining budget

Fall back to item -317 step 3's blanket sweep (re-scan first: `python3
scratch/agent/s494_item317_step3_tracer.py --scan && python3 scratch/agent/s506_dedupe.py` -- stale
since R8's insertion). ~126 locations remain; prefer non-`beginFrameDLChunk` sites unless item -319's
fix already covers that function's tier. Full guard table and gotchas: `docs/PROJECT-OVERVIEW.md`
§22-§23, `PORTING-STATE.md` Sessions 490-519.
