# NEXT work unit

HYPOTHESIS-ID: item-316-5bb4-struct-family-shape-check

## s488 summary: item -314 fully CLOSED 2/2, fresh idiom scan closed the large-bucket method, M5 lead-check cleared

Item -314's 2nd independent confirm (`s487_audio_voice_baseptr_loop_confirm`, folded in from the loop
queue) came back the cleanest possible outcome: **zero `[CRASH]` events over the entire run**, 0
fires on any guard family, `hangarbay-entry` positive control at n=3000. Item -314 is now fully
CLOSED, 2/2. All four items from the s481-487 arc (-312/-313/-314/-315) are done.

Ran the recommended fresh M3 idiom scan (`N64Recomp/scratch_s488_scan.py`, the s465/s477 precedent
with an extended exclude list). The `>=20`-site tier came back structurally dry — every large bucket
is already a named guard or already classified. **This closes the large-bucket lui+lw/lui+sw
idiom-audit method for now.** Also cleared the overdue M5 lead-check (re-read `M5-AUDIO-PLAN.md` +
scanned PORTING-STATE Sessions 481-487): no new stub/trap/gate surface found, M5 remains DONE.

## This session's next work unit: item -316's `-0x5BB4` candidate

Lowering the scan threshold to 10-19 sites surfaced one real candidate: `hi16=0x8012,offset=-0x5BB4`
(19 sites, `funcs_3.c`/`funcs_4.c`). It sits in the same struct family as three already-guarded
siblings within 0x70 bytes (`-0x5824` DL_LIST_RESET, `-0x5BBC` MATERIAL_ARRAY_PTR, `-0x5B48`
NODE_LIST_HEAD), is both READ and WRITTEN (write at `funcs_3.c:4702`), and at one read site
(`funcs_4.c:1492-1512`) the raw reload is copied straight into an output struct's field `0x4` with no
validation — the same "propagate-an-unvalidated-reload" shape as the items -312..-315 arc. Only 1/19
sites has been read so far — below this lineage's own 2-site confirmation standard.

**Steps** (same standard every prior bucket in this lineage has used):
1. `grep -n "5BB4" N64Recomp/RecompiledFuncs/funcs_3.c N64Recomp/RecompiledFuncs/funcs_4.c` — find
   all 19 sites (call sites list already partially known from `scratch_s488_scan.py`'s output; rerun
   it for the full site list, `python3 N64Recomp/scratch_s488_scan.py` — the funcs_3/4.c examples are
   printed for the bucket).
2. Direct-source-read a 2nd site (the first was `funcs_4.c:1480-1512`, `initSomethingFn`-adjacent —
   identify the actual function name via `grep -B30 "0x8001050"` for the enclosing `RECOMP_FUNC`
   line). Confirm the shape: is the reloaded value a pointer, and does whatever consumes it
   (`MEM_W(0X4, ctx->r4) = ctx->r3;` in the 1st site — an OUTPUT STRUCT WRITE, not a direct deref)
   get dereferenced by a CALLER? Trace `funcs_4.c`'s enclosing function's callers (grep the function
   name across `funcs_*.c`) to see if the output struct's field 0x4 is read back as a pointer anywhere
   downstream — that's the actual risk, not the reload itself.
3. If the shape confirms a real risk (same "unguarded reload feeds an unvalidated pointer write/deref"
   pattern as -312/-313/-314/-315): design a guard (likely a simple `!= 0` or address-range check
   before the copy/deref, matching the style of `DL_LIST_APPEND_RWRITE_GUARD`) and apply via
   `fixup_game_funcs.py`.
4. If the shape does NOT confirm a risk (e.g. field 0x4 is never read back, or it's a benign integer
   the "pointer-shaped" match is coincidental): CLASSIFY AND CLOSE item -316 as a false lead, same as
   several -30x items, and move to the next fresh idiom-scan session (re-run
   `scratch_s488_scan.py` after any future guard additions to catch newly-exposed buckets, or resume
   the `lui`+`sw` angle at the 10-19 tier if `lui`+`lw` is now fully mined).

## Regen/build/soak recipe (only needed if item -316 becomes a real fix — this analysis step needs neither)
`python3 -c "import glob,os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
→ `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` → `cd ~/Documents/Tools/N64Recomp
&& ./build/N64Recomp rogue_squadron.toml` → `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py`
(check the report for the expected counts, no errors) → **`cd
/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build`** (NOT `~/Documents/Tools/N64Recomp/build`
— that's the recompiler CLI's own build and silently no-ops, the s487 build-dir mistake) →
`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`. Arm every sibling
guard env var per the standing rule — see `scratch/agent/soak_queue/done/s487_audio_voice_baseptr_loop_confirm_20260807-201244.sh`
for the current full list, add `ROGUESQ_LOG_<NEW_GUARD_NAME>=1` for whatever item -316's guard is
named.

## Soak queue status
Empty — the s487 confirm was the last queued item, now folded in. Nothing queued.
