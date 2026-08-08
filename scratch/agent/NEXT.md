# NEXT work unit

HYPOTHESIS-ID: item-314-audio-slot-active-guard-idiom-class-fix

## s483 summary: closed item -313 (2/2 confirms), then found item -314 -- AUDIO_SLOT_ACTIVE_GUARD
(s166)'s "unique address" claim was ALSO address-only, not shape-wide, same as item -312/-313

Picked up an interrupted prior session (STATUS was `WORKING`, CURRENT-TRUTH.md had uncommitted
s483 analysis but no PORTING-STATE.md entry / NEXT.md update / commit). Re-verified its finding
independently from the raw soak logs (did not just trust the draft text): `s482_blanket_rwrite_guard_confirm`
ran `rc=3` (crashed) but 0 fires on `dl-list-append-rwrite-guard` or any of the 6 sibling guard
families, `hangarbay-entry n=33` positive control, crash was `pc-symbol=coalesceFreeHeapBlocks+2016`/
`last-guest-pc=0x800023b0` -- byte-identical to the already-closed s354-366 heap-coalesce family
(verbatim address match, `PORTING-STATE.md` ~line 33370). **Item -313 is fully CLOSED, 2/2
independent confirms clean; the whole `DL_LIST_APPEND_GUARD` lineage (items -291, -312, -313) is
done.**

M5 lead check skipped (below the 3-session re-check threshold). Fell through to M3 idiom-class
audit resumption per NEXT.md's own fallback option (a): applied item -313's "grep-verified unique
ADDRESS is not grep-verified unique SHAPE" skepticism to other closed site-anchored guards.
Delegated a survey (Explore agent) that ranked 9 candidates; picked the top one,
`AUDIO_SLOT_ACTIVE_GUARD` (s166, `isAudioSlotActive`, item `-159..-14` mega-bucket). Its own
comment claims "Guest addresses 0x80092110/0x80092114 confirmed unique ... via grep" -- true of
those two literal addresses, never checked for the SHAPE recurring elsewhere.

**Found it does, at scale.** The guarded global (`0x801496F8`, `lui $reg,0x8015`/
`lw $reg,-0x6908($reg)`, written once in `allocateSongChannelArray` funcs_23.c:10785) is loaded at
**21 total sites** in `funcs_24.c`. Only 1 (`isAudioSlotActive`, 0x80092100) is guarded. The other
**20 span 15 different MusyX voice-management functions** (full list + line numbers:
`docs/CURRENT-TRUTH.md` item -314, `PORTING-STATE.md` Session 483). Confirmed via 2 direct source
reads beyond the known site (`musyxMixActiveVoices` funcs_24.c:2540-2564, `deactivateVoice`
funcs_24.c:6643-6657) — both dereference the loaded pointer at a computed `idx*136` offset with
ZERO validation, same bug class, different addresses, different functions each time. Filed as item
-314, CLASSIFIED AND DEFERRED — not fixed this session because it is NOT a uniform blanket-regex
case like item -313's 84 identical sites: this idiom recurs across 15 functions with different
downstream instruction shapes after the load. Verified `MEM_W`/`MEM_BU` in
`N64Recomp/include/recomp.h`: a bad pointer can NOT simply be zeroed (`rdram + (0 - 0x80000000)` is
still a wild host pointer), so the fix needs the same "skip only the guarded op" if/else wrapper
`GENERIC_CACHE_GUARD`/`DL_LIST_APPEND_GUARD_RWRITE` already use, not `isAudioSlotActive`'s own
early-`return` bail (that only works because `isAudioSlotActive` is a whole-function boolean
check; the other 15 functions are not).

## This session's top work unit: design and implement item -314's fix

1. Re-open `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c` (generated;
   regenerate via `make_elf.py -> N64Recomp` first if it's not already the post-fixup version) and
   read all 20 unguarded sites listed in `docs/CURRENT-TRUTH.md` item -314 (line numbers current as
   of s483; may shift slightly after a fresh regen, re-locate by the `-0x6908` grep, NOT by line
   number). For EACH site, record: the exact register combine chain (which registers, `sll`/`addu`
   sequence) and the exact deref instruction(s) immediately following (offset, width, read vs
   write, single vs multi-field).
2. Group sites into shape buckets, same method as `DL_LIST_APPEND_GUARD`'s "bucket A vs bucket
   B/C" split (item -313 precedent). The dominant shape observed so far:
   `lui;lw(-0x6908);sll(<<4);addu;sll(<<3);addu` then an immediate deref — likely covers most of
   the 20. At least `musyxInitVoiceFromSample`'s 3rd site (line ~6097 pre-regen) interleaves an
   unrelated `lui $at,0x8004`/`lwc1` float-constant load between the combine and the deref — expect
   more sites like this; find them all before writing the regex, not after.
3. Write ONE (or a small number of) `re.compile` blanket patch(es) in
   `N64Recomp/fixup_game_funcs.py`, function-scoped to each named function (or file-scoped to
   `funcs_24.c` if the shape is truly uniform across all of them), following the EXACT if/else
   "skip only the guarded chain, else proceed with original instructions" template
   `_generic_cache_guard_patch`/`_dl_list_append_guard_patch` use (fixup_game_funcs.py ~line
   14197/14330) — capture the load, the combine, AND the deref instruction(s) in one regex so the
   guard can wrap the WHOLE dependent chain, not just the load. New env var/log tag:
   `ROGUESQ_LOG_AUDIO_VOICE_PTR_GUARD` / `[audio-voice-ptr-guard]` (do not reuse
   `ROGUESQ_LOG_AUDIO_SLOT_ACTIVE_GUARD` — that one stays scoped to its own single site).
4. Regen order: `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake` (mandatory, hand edits
   to generated code do not survive a regen). Verify the patch report shows exactly the expected
   site count (target: up to 20, may be less if some sites turn out already-safe on closer read —
   do NOT force a match count, report what's actually found) and that all sibling guard families'
   counts (`GENERIC_CACHE_GUARD` 107, `DL_BUFFER_POOL_GUARD` 84, `SIBLING_PTR_WRITE_GUARD` 120,
   `DL_LIST_RESET_GUARD` 84, `FREELIST_NEXT_GUARD` 105, `DL_LIST_APPEND_GUARD`/`_RWRITE` 84,
   `AUDIO_SLOT_ACTIVE_GUARD` 1) are unregressed.
5. Full clean cmake build (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake ...`).
6. Manual foreground soak (positive control: `hangarbay-entry` reaches, `ROGUESQ_LOG_AUDIO_VOICE_PTR_GUARD=1`
   armed) + queue a 2nd independent confirm soak to `scratch/agent/soak_queue/`, arming ALL passive
   breadcrumb/instrument env vars per the standing rule.

## Fallback if the shape turns out too varied to safely blanket-patch this session

If sites 3+ show genuinely incompatible downstream shapes (not just "one interleaved instruction"
but structurally different multi-branch code), do NOT force a one-size regex. Fix the dominant
bucket only, leave the outliers explicitly enumerated and unfixed with a follow-up item, and say so
plainly in the session write-up — partial coverage with an honest list beats a regex that silently
skips sites it doesn't actually match.

## Soak queue status

No soaks currently queued (the `s482_blanket_rwrite_guard_confirm` recipe already ran and closed
item -313; it should be moved to `scratch/agent/soak_queue/done/` if not already there). This
session's own confirm soak for item -314's fix goes to `scratch/agent/soak_queue/` per step 6 above.
