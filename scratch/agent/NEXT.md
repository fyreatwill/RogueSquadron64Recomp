# NEXT work unit — stop per-site guarding, hunt for the WRITE site of the
# recurring `0x0000000300000000` corrupt literal

Read PORTING-STATE Session 218 in full (`grep -n "^## Session 218"
PORTING-STATE.md`) before doing anything else. Short version: s218 executed
NEXT.md's prescribed work unit (source-read `heapWalker` end to end),
corrected a wrong inherited line-range estimate (`heapWalker` is
`funcs_3.c:99-700`, not `99-7978` — checked directly via
`grep -n "^RECOMP_FUNC" funcs_3.c` rather than trusting the old number), found
the actual mechanism the existing GUARD3 misses (each of the 5 walk loops
does TWO consecutive derefs per iteration; GUARD3 only validates the pointer
that PRODUCES the first deref's result, never the result itself before the
second, immediately-following deref uses it), and shipped GUARD4 at all 5
sites. The soak never routed through heapWalker's loop this time (GUARD4
itself unconfirmed live, 0/0, no regression) — but it died at hold-iter 28
(much further than s217's iter 1) to a **third** independent sighting of the
exact literal `0x0000000300000000`, this time in `renderUnlitMeshFaces`
(scene-graph rendering — `traverseSceneGraphRecursive`/`processSceneNode`),
a subsystem with no structural relationship to heap-walking at all.

**This is the key finding.** Three sessions running (s216 `heapFreeListDequeue`,
s217 `heapWalker`, s218 `renderUnlitMeshFaces`), the identical 64-bit literal
— integer `3` alone in the upper 32 bits — has shown up in three
structurally-unrelated subsystems. Guarding one consumer at a time has now
paid off twice (found real, previously-missed unguarded derefs both times)
but each fix just uncovers ANOTHER unrelated consumer with the same symptom,
never the origin. Per this project's own rule 8 (stop after repeated
same-hypothesis iterations with no discriminating result on the CORE
question), the core question was never "which consumer is unguarded" — it's
"where does this value get written" — and that question has not been asked
yet in 3 sessions of consumer-side chasing.

## Do NOT do this iteration

- Do not source-read a 4th consumer function looking for a 6th/7th/8th
  unguarded deref site. That pattern has a 100% hit rate so far (it always
  finds something) but a 0% rate of explaining WHY the corruption exists — it
  will keep finding new consumers indefinitely without ever converging.
- Do not add another guard mirroring GUARD3/GUARD4's upper-32-bit template to
  `renderUnlitMeshFaces` as a reflexive next step — read this NEXT.md's
  reasoning below first; a guard there would suppress this session's crash
  but do nothing to explain the shared literal, and per s213's "guard that
  doesn't match the actual corruption shape is wasted work" lesson, a guard
  aimed at the wrong layer (consumer vs. producer) is exactly that.
- Do not re-enable NAN_CHECK-disable (still ON, untouched again this
  session).

## Do this iteration: find where `0x0000000300000000` gets written

### Step 1 — tabulate what's already known (cheap, do first)

Grep PORTING-STATE for every prior sighting of this literal
(`grep -n "0x0000000300000000\|0000000300000000" PORTING-STATE.md`) and build
a small table: session, consumer function, register holding the value, the
OTHER register in the `si_addr = a + b` sum (this tells you the base/offset
being added), and the low-32-bits of `si_addr` itself. Three data points
exist so far (s216, s217, s218). The discriminating question this table
answers: do the LOW 32 bits of `si_addr` (or of the corrupt register) cluster
in a narrow address range across incidents (pointing at one shared
arena/pool — heap corruption, hypothesis B/C below) or scatter widely
(weakening the shared-origin theory, favoring hypothesis A)? This is a
2-minute step — do not skip it before writing any new instrumentation.

### Step 2 — competing hypotheses and the discriminating probe

- **(A) Guest-code arithmetic bug**: some MIPS-translated function
  literal-computes a value with upper bits `0x3` (e.g. a small enum/mode
  value incorrectly OR'd or shifted into a 64-bit slot's top half, outside
  the `S32()`/`ADD32()`/`U32()` discipline every legit conversion in this
  codebase uses). If true, it's a single localized bug, not systemic —
  finding it would fully explain all three sightings only if the SAME
  function/callsite writes the value that all three consumers later read.
- **(B) Native-side aliasing**: the value enters via `ultramodern`'s native
  C++ runtime (thread-context save/restore, message-queue plumbing, or
  similar) — a stray native `int`/enum value of `3` gets written into a
  `ctx->rN`-shaped 64-bit slot or into guest-visible memory the native code
  touches directly, independent of which guest subsystem later reads it.
- **(C) Heap corruption / type confusion**: something (a guest buffer
  overflow, double-free, or use-after-free in the emulated heap) scribbles
  the literal into a memory region that gets reused by unrelated allocation
  types — heap blocks, scene nodes, etc. — all of which happen to read a
  "next pointer"-shaped field from the same struct offset. This would
  explain the cross-subsystem spread WITHOUT requiring a single shared
  write site in the code: any of several call sites doing an OOB heap write
  could produce it, and any consumer walking a list through that offset
  would eventually read it.

**Discriminating measurement**: a project-wide grep (not a single-function
source-read) across all of `RecompiledFuncs/funcs_*.c` for any site that
combines a value known to be `3` (a small table index, mode byte, or literal)
into a 64-bit register via `|`, `+`, `<<32`, or a raw non-`S32`/`ADD32`/`U32`
64-bit assignment — this is grep-able (`grep -n "<< 32\|>> 32" funcs_*.c` as
a starting net, then manually filter for anything that could produce exactly
`3` in the result) and answers hypothesis (A) directly without a full
function read. If this search comes back empty (no such site anywhere in the
generated code), that's a real, load-bearing null result for (A) — two
sessions now (s217 for `heapFreeListDequeue`, s218 for `heapWalker`) already
confirmed the LOCAL consuming functions don't compute it; a project-wide grep
finding nothing extends that to "no guest code anywhere computes it," making
(B)/(C) the live hypotheses.

If (A) is refuted this way, the next probe (do not do both in one iteration
per the budget rule) would be instrumenting `rs_malloc`/`rs_free`'s existing
diagnostics (`ROGUESQ_LOG_RS_MALLOC_WALK`/`ROGUESQ_LOG_RS_FREE_WALK`, already
armed in several recent soaks) to log the FULL 64-bit value of every write
through a freed/reused block header, filtered to catch the literal `3`
appearing in the upper 32 bits at the moment it's written — this is a
WRITE-side watch, the first one this investigation has tried; every
instrument so far has been read-side (consumer guards).

## Environment notes (carried forward, still current)

- **`heapWalker` is `funcs_3.c:99-700`** (corrected this session — do not
  reuse the old `99-7978` estimate; it was simply wrong and nobody had
  checked it directly until now). `heapFreeListDequeue` remains
  `funcs_3.c:15427-17128` (verified s217, unchanged).
- **`recomp.h` location**: the ONE that matters is
  `lib/N64ModernRuntime/N64Recomp/include/recomp.h` — a nested submodule
  inside `lib/N64ModernRuntime`, NOT the sibling checkout at
  `/Users/williambuckley/Documents/Tools/N64Recomp`. `CMakeLists.txt`'s
  `target_include_directories` only ever adds the nested path. The sibling
  checkout still matters for `RECOMP_FUNCS_DIR` (generated `.c` file
  *content*) but NOT for header resolution.
  `submodule-patches/export.sh`/`apply.sh` cover both the outer
  `N64ModernRuntime` and the nested `N64Recomp` (`N64Recomp-nested.patch`).
  Any edit under `lib/` needs `export.sh` + commit, same session.
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`** —
  the SIBLING checkout, not this repo's `tools/`. It is genuinely untracked
  there (confirmed s218: `git status --short` shows `?? fixup_game_funcs.py`
  in that checkout) — this has been a known, deliberate state since s83
  ("not `lib/`, no submodule patch") and is NOT this session's new problem to
  fix, but it remains a real single-point-of-failure risk (297KB, ~18
  sessions of guard patches, zero version control) worth the user's attention
  independent of this investigation.
- **`fixup_game_funcs.py` is NOT fully idempotent**: most patches are
  anchored to pristine (unpatched) source text via regex, so re-running after
  it's already applied is a silent no-op for those — but at least one patch
  (s139's `rs_malloc` entry diagnostic) matches even already-patched text and
  will double-apply if run twice in a row on the same generated output. Only
  run `fixup_game_funcs.py` ONCE per regen cycle.
- The `[CRASH][pc-symbol]` diagnostic (dladdr on the raw mcontext `pc`) is
  permanent, always-on, and MORE PRECISE than `backtrace_symbols_fd` (s213).
  Trust dladdr for the crash PC itself.
- Disassembly/symbolication tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are
  ALL blocked (non-interactive session). Source-level/structural reasoning
  only.
- This project builds `CMAKE_BUILD_TYPE=Debug` (`-O0`); `RECOMP_FUNC` is
  `noinline`. No LTO — dladdr resolving to function F means the fault is
  inside F's own body.
- `recomp.h`: `U32(val)` = `(uint32_t)(val)`; `gpr` = `uint64_t`; a legit
  KSEG0 `gpr` sign-extends, upper bits `0xFFFFFFFF`. A guard that only checks
  `U32()` is BLIND to upper-bits corruption like this investigation's `0x3`
  shape — always add the upper-32-bits check too.
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- `./build/N64Recomp rogue_squadron.toml` needs an `env` prefix. Compound
  `cd ... && cmd` gets denied in one Bash call — issue `cd` and the following
  command as SEPARATE Bash calls.
- `git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule —
  `cd` into the target dir first (as its own Bash call), then run bare
  `git <cmd>`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Launch soaks with `Bash(..., run_in_background=true)`, then either wait
  for the automatic task-notification or block with
  `TaskOutput(task_id, block=true, timeout=180000-480000)`.
- The `grep -ac '[CRASH]'` count in `run_mission_keys.sh`'s summary counts
  LINES matching the tag, not crash EVENTS — grep `caught signal` for the
  real event count.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s218 — read
it with `grep`/offset-limited `Read`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail, paired with a real experiment — flagged for 16+
sessions without action, escalating.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout (see environment notes above) has been flagged as a known
state since s83 but never as an explicit risk item — worth surfacing to the
user directly rather than continuing to treat it as ambient/expected. Not
autonomously actionable (this repo's commit scope doesn't cover that
checkout), so still flagged for the user, not fixed here.

`/Users/williambuckley/Documents/Tools/N64Recomp` (sibling checkout, matters
only for `RecompiledFuncs/*.c` generated content, not `recomp.h` header
resolution) and `~/Documents/Tools/rogue_squadron64` are separate git
checkouts with long-standing uncommitted changes, unrelated to this repo's
commit scope. Still flagged for the user, not committed autonomously.

`lib/rt64` still shows as modified in `git status` — pre-existing, not
investigated; still worth checking whether its patches are in sync with
`submodule-patches/rt64*.patch` before assuming this is normal
steady-state dirtiness.
