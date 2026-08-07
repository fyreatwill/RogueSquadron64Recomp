# BLOCKED (s454)

## What happened

s454 found a genuine, previously-unaudited M3 idiom class (`-0x5824($reg)` → fixed global
`0x8011A7DC`, a doubly-linked-list append with no existing bounds check, 57 verified byte-identical
sites in `funcs_3.c`/`funcs_4.c` — same crash-history-bearing display-list-emission code cluster as
4 already-fixed sibling families protecting a different global). Designed and wrote a guard
(`DL_LIST_APPEND_GUARD` in `N64Recomp/fixup_game_funcs.py`, untracked, syntax-checked) but did
**not** run it through regen/build/live-verify/soak/commit.

## Why it's blocked

Partway through the session, real-time evidence accumulated that `tools/agent/loop.sh` was already
running a LIVE, independent autonomous iteration concurrently, doing what looks like the identical
mandate:

1. `scratch/agent/loop.log` logged "iteration 2 starting" at the exact moment s453 committed
   (`fe67d73`, 10:30:16), with no completion record as of investigation (15+ minutes later).
2. `ps aux` showed a live spawned `claude --model claude-fable-5 --resume=...` process plus its
   `loop.sh`/`caffeinate` parent tree, still running.
3. A scratch file this session wrote (`N64Recomp/scratch_s454_scan.py`) was independently
   rewritten mid-session, in place, by that other process into a more polished equivalent of the
   same discriminating scan — direct proof of concurrent, uncoordinated work on the same file.
4. `N64Recomp/RecompiledFuncs/*.c` (50 files) was observed EMPTY mid-session, then repopulated by
   a fresh regen+fixup cycle timestamped after this session's own investigation began, and that
   regen did NOT contain this session's `DL_LIST_APPEND_GUARD` patch — proof a different process
   ran its own full regen/fixup on the same shared files during this session's window.

`CLAUDE.md` states explicitly: "One game run at a time. Parallelism goes into offline analysis and
docs only." `N64Recomp/fixup_game_funcs.py`, `RecompiledFuncs/*.c`, and `build/` are all shared,
non-git-tracked, single-writer-assumed state with no merge safety net (no version control, no
locking). Running `make_elf.py`/`N64Recomp`/`cmake build`/a live game process from this session
while another live session is doing the same would risk actual file corruption or a corrupted
build/game-process collision, not just wasted duplicate analysis — a categorically worse outcome
than stopping short.

## What I need from a human

1. **Confirm whether `loop.sh` should be running standalone iterations at all while a
   manually-spawned single-iteration session (like this one) is also active** — if both are
   expected to run, some coordination mechanism (lockfile, or don't double-spawn) is needed before
   the next session; if only one should ever be running, check why both were live here.
2. Check `git log -5 --oneline` in the main repo for whatever `loop.sh`'s own iteration 2
   ultimately committed (it may have finished by the time this is read) — reconcile against this
   session's finding (item -291 in `docs/CURRENT-TRUTH.md`) before assuming the `-0x5824`
   idiom-class work is still the top priority; the other process may have already covered it, or
   found something else entirely.
3. Once exclusivity is confirmed for a future session, the actual work
   (build/verify/soak the already-designed `DL_LIST_APPEND_GUARD` patch) is a same-day,
   low-ambiguity task — full exact commands are in `scratch/agent/NEXT.md`.

## What I already tried

Completed the full discovery-and-design phase safely (static analysis, reading, and a Python
scratch script — none of which touch shared mutable build state): built a discriminating scan,
ruled out the noise floor (generic pointer-chasing at small offsets), found and verified the
`-0x5824` class by direct code reading (not just counting), confirmed the canonical shape at
57/57 sites programmatically, and wrote a syntactically-valid guard patch mirroring the established
`FREELIST_NEXT_GUARD`/`CACHE_HEAD_A1_GUARD` "skip the write, don't substitute a value that would
crash one line later" precedent. Stopped at the regen/build boundary specifically because that's
where the collision with the concurrent process becomes destructive rather than just wasteful.
