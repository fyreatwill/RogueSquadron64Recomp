# NEXT (s7366): idiom-class audit - class AQ, host containers touched from two threads without a common lock
HYPOTHESIS-ID: host-container-race
Context: s7365 (class AP) closed; its one upstream hole left open (rt64_texture_cache fileSystemStreamResolvedPaths cleared at 1526
under no mutex while the upload thread reads it at 1071) is the race shape, not the lifetime shape. Class AQ: a std container / member
written in one thread's function and read or written in another's, where the two sites do not hold the same mutex (lock_guard /
unique_lock / scoped_lock on the same mutex name in the enclosing scope).
NOTE: CURRENT-TRUTH is 59985 bytes; if Step 0 prints > 60000 this iteration is MAINTENANCE instead.
Hypotheses: H-safe (same lock, or single-threaded by construction: e.g. only the game thread), H-ordered (handoff through a queue/
atomic/condition with happens-before), H-race (fix: lock or move ownership).
Method: tools/s7366_race_census.py: thread entry points (std::thread / SDL_CreateThread / ultramodern thread bodies / RT64 worker
loops: Workload/Present/Texture upload / rsp audio) -> one-level same-file call closure -> container members each touches, with the
mutexes held at each site (lock objects in enclosing blocks). Rows: member touched from >=2 thread roots with no common lock.
Planted selftest rows (two thread lambdas, one shared vector, lock in one only = B; both locked = SAFE).
Independent reviewers per file group (code + rows, not conclusions). Real races on default paths: fix + TSan arm (clang -fsanitize=thread
on a unit repro like tools/s7365_ap_ctl.sh) + 260 s dd8 smoke `env SECS=260 zsh scratch/s7326/run.zsh s7366_dd8 ''`.
Side question carried from s7364/s7365 (cheap, do first): what did the stale tile DRAW? Same dd8 recipe, presented-frame captures
ROGUESQ_S7364_WLRESET=0 vs default phase-gated on the same VI ordinals; if frames differ, compare against angrylion (tools/oracle).
Exit: PORTING-STATE s7366, CURRENT-TRUTH 27ze -> closed, commit; any lib/ edit -> ./submodule-patches/export.sh first.
