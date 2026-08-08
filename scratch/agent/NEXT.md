# NEXT work unit

HYPOTHESIS-ID: item-317-step3-183-site-blanket-sweep

## Maintenance note
`docs/CURRENT-TRUTH.md` is now 60,657 bytes (over the 60,000 trigger, pushed over by this session's
item -317 updates). **The next iteration is a MAINTENANCE iteration per Step 0 of ITERATION.md** —
compact CURRENT-TRUTH toward ~35KB before picking a new work unit. Do NOT run experiments in that
iteration.

## s492 summary: item -317 step 1 (heapFreeListDequeue) fully CLOSED 2/2; step 2
(buildOrientedFaceGeometry, funcs_4.c) traced and fixed, 1st confirm clean, 2nd queued

s491 left one soak queued (`s491_heap_dequeue_blockskip_confirm.sh`) and one explicit deferral (the
`funcs_4.c` `buildOrientedFaceGeometry` sibling site, NOT to be fixed by blindly reusing the
`heapFreeListDequeue` shape). s492 did both:

1. **Consumed the queued confirm**: 0 `[CRASH]` events over the full 300s run (cleanest possible
   outcome), effectively 0 fires on `HEAP_DEQUEUE_DERIVED_PTR_GUARD`, `hangarbay-entry` n=35
   (positive control). Item -317 step 1 is FULLY CLOSED, 2/2.
2. **Traced `buildOrientedFaceGeometry`'s `ctx->r18` provenance directly** (read funcs_4.c
   9160-11655 in full) rather than trusting the s490 subagent's summary. Found: `ctx->r4` reloads
   unguarded from the SAME free-list-cache-head global (`0x801163B0`) at `0x80012E94`, survives
   through four existing sibling guards untouched (none revalidate `r4`), propagates into `ctx->r18
   = ADD32(ctx->r4, 0X8)` at `0x80012EF0`, dereferenced unguarded across an 8-field struct-init block
   (`0x80012F14`-`0x80012F94`). The multi-path hazard (`goto L_80012F08` at `0x80012E24`) resolved to
   a clean 2-entry join (exactly one goto + one fallthrough into the label) — validated `ctx->r18`
   itself at the join, block-skip to the existing epilogue label `L_80012F98` on invalid. New guard
   `ORIENTED_FACE_DERIVED_PTR_GUARD`. Build-verified clean, 1st live-verify: 0 fires on the new
   guard, `hangarbay-entry` n=31 (positive control), crashed on the already-catalogued
   `initVec4TripletFromArgs+68`/`last-guest-pc=0x800ab068` family (unrelated, same as s489/s463/
   s468). 2nd confirm queued (`scratch/agent/soak_queue/s492_oriented_face_derived_ptr_confirm.sh`).

## This session's next work unit (AFTER the maintenance pass above)

Item -317's remaining open scope is **step 3: the wider 183-site blanket sweep** of the
`ctx->rL = MEM_W(ctx->rL, 0X63B0)` free-list-cache-head reload idiom across `funcs_3.c`/`funcs_4.c`.
s490's textual-proximity classifier already proved untrustworthy (it structurally cannot detect the
shared-label-merge hazard that bit s490's own first fix attempt on the very first site it tried) —
do NOT repeat that approach at scale. This needs either:

1. **Control-flow-aware tooling**: for each of the 183 sites, trace the register actually
   dereferenced (not the reload target) forward to its true derefs, and backward from each deref to
   confirm every path that reaches it has consistent, already-validated provenance — essentially
   automating what s490/s491/s492 did by hand for 2 sites. Worth scoping as a scripted pass (Python,
   in the N64Recomp repo alongside the prior `scratch_s465_*` scan scripts) rather than 181 more
   manual traces.
2. **Alternatively**: wait for the next breadcrumb/soak crash to surface a THIRD instance
   organically (as items -316→-317 and -317 step2 both were found), and fix opportunistically rather
   than sweeping blind.

Given the manual-trace cost per site (this session's step 2 took a full iteration for ONE site), a
scripted control-flow tracer is probably the better expected-value move IF time allows — but this is
a new tool-building task, not a single guard fix, so scope it as its own work unit with its own
positive control (verify the tracer correctly flags the 2 already-known-bad sites and correctly
clears a sample of known-benign sites) before trusting its output at scale.

If step 3 is judged too large for one iteration, fall back to: a fresh frequency-scan angle (both
`lui`+`lw` and `lui`+`sw` are structurally dry at the >=20-site tier per s488), or the M5 lead-check
cadence (last checked s488, due after 3+ more sessions).

## Regen/build/soak recipe
`python3 -c "import glob,os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
→ `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` → `cd ~/Documents/Tools/N64Recomp
&& ./build/N64Recomp rogue_squadron.toml` → `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py`
(check the report for expected counts, no errors, no SKIPPED lines other than the known-permanent
S392_H3A/H3B item -290 remainder; the script now REFUSES a second run on already-patched files via
its own `RS64_FIXUP_APPLIED` marker — regenerate from scratch if you need to re-run it) → **`cd
/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build`** (NOT `~/Documents/Tools/N64Recomp/build`
— that's the recompiler CLI's own build and silently no-ops) →
`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`. Arm every sibling
guard env var per the standing rule — see
`scratch/agent/soak_queue/s492_oriented_face_derived_ptr_confirm.sh` for the current full list.
Live-verify BEFORE queueing a 2nd confirm and BEFORE folding into the ledger.

## Soak queue status
1 item queued: `s492_oriented_face_derived_ptr_confirm.sh` (item -317 step 2's own fix, 2nd
independent confirm).
