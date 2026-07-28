# NEXT work unit — get a 2nd occurrence of s194's new processSceneNode-
# adjacent crash, then localize and guard it

Read PORTING-STATE Session 194 in full before doing anything else (`grep -n
"^## Session 194" PORTING-STATE.md`); this file only has the actionable
summary. Also read docs/CURRENT-TRUTH.md's `-43` next-steps item (top of the
list).

## Why this is the next work unit (read before doing anything else)

s194 confirmed disassembly tools (`otool`, `objdump`) are STILL blocked in
this non-interactive session (denied again, same as s193) — do not
re-attempt a 3rd time this session unless something about the environment
has visibly changed (e.g. check `.claude/settings.json` for a new allow
rule first).

Instead, s194 found the POSIX crash handler (`src/main/main.cpp:1654-1683`)
was silently discarding its own `siginfo_t*`/`ucontext_t*` despite
requesting `SA_SIGINFO`. Fixed that: it now prints `si_addr`/`si_code` and
the full ARM64 register file (`x0`-`x28`, `fp`/`lr`/`sp`/`pc`/`cpsr`,
`far`/`esr`) on every SIGSEGV/SIGBUS/SIGABRT, no rebuild or env var needed
going forward — this is now a permanent, always-on diagnostic.

The FIRST soak with it (`scratch/agent/run_mcontext1.sh`, tag `mcontext1`)
did two things at once: (1) confirmed the instrument via positive control
(`si_addr==far`, internally-consistent register decomposition), and (2)
reached decisionN=9741 — the furthest of ANY soak to date, and the first
time any soak has gotten INSIDE the `[scene-node-ptr-guard]` target window
(9660-9792). It crashed there on a NEW, previously-uncatalogued bug before
the guarded site could fire (`[scene-node-ptr-guard]` still 0/4 across all
soaks — the s190 fix remains completely untested).

The register evidence is unusually clean for a first look: `far` (fault
address) == `x0/x8 (0x300000000, almost certainly the rdram host base
pointer) + x9 (0x80630062, a raw guest pointer that still has its KSEG0 tag
`0x80000000` and is zero- not sign-extended)`. Compare `N64Recomp/include/
recomp.h`'s `MEM_W` macro, the normal/correct path: `rdram + ((reg +
offset) - 0xFFFFFFFF80000000)`, which only works because `ADD32` sign-
extends 32-bit register values to `0xFFFFFFFF80xxxxxx` first. Here, some
OTHER code path added the raw, unmasked, zero-extended guest address
directly to the rdram base with no KSEG0 subtraction at all, producing a
~2 GB wild pointer. `lr=processSceneNode+8772` (`N64Recomp/RecompiledFuncs/
funcs_4.c:13759-14873`) is the return address of the call to whatever
actually faulted — the unwinder couldn't resolve a symbol for the real
`pc`, meaning it's very likely a small/leaf helper with no separate stack
frame, called from inside `processSceneNode`'s body.

This is **single-source, first occurrence** — `grep -l "processSceneNode +
8772" scratch/s73_post_a_scene/*/run.log` matches only the `mcontext1` run.
Iron rule 4 (two independent lines of evidence) is not yet satisfied. Do
NOT write this into CURRENT-TRUTH as a confirmed root cause; it's a strong,
well-characterized lead.

## Do this, in order

1. Re-run the SAME soak config (copy `run_mcontext1.sh` to a new tag,
   e.g. `mcontext2` — re-running the same tag overwrites the log) to see if
   the `processSceneNode + 8772` / `far = rdram_base + 0x80630062`-pattern
   crash recurs. Discriminating outcomes:
   - **Recurs at the same or a similar decisionN, same signature** → this
     is now the dominant soak-blocker in the target window (promote it in
     CURRENT-TRUTH the way `queueGPUUploadTMEM` was promoted after s191/
     s192), and the localization work below becomes high-value.
   - **Doesn't recur, soak dies to something else (or reaches further)** →
     treat as one-off soak variance for now; don't sink further budget into
     localizing a single occurrence. Check instead whether `[scene-node-
     ptr-guard]` finally fires (the actual target question).
   - **Doesn't recur, soak reaches PAST 9792 and `[scene-node-ptr-guard]`
     fires** → the primary open question (does the s190 fix work) is
     FINALLY answered. This is the best possible outcome — write it up as
     the headline finding.
2. If it recurs (or even on this one occurrence, if budget allows after
   step 1): try to localize the unmasked-pointer call site. Read
   `processSceneNode` in full (`N64Recomp/RecompiledFuncs/funcs_4.c:13759-
   14873`) looking for any call to a helper function or any raw pointer
   arithmetic that does NOT go through `MEM_W`/`MEM_H`/`MEM_B`/`ADD32` (i.e.
   anywhere a 32-bit value derived from `ctx->rX` gets used as a byte
   offset or added to `rdram` directly without the sign-extend-then-
   subtract pattern). Cross-reference against the MIPS address comments
   (`// 0x800150xx: ...`) to map back to the actual instruction. This is
   real, bounded source-reading work — budget it, don't guess blind.
3. Once localized with actual confidence, add a getenv-gated, bounded-
   counter guard (mirrors `[scene-node-ptr-guard]`'s pattern) either in
   `N64Recomp/fixup_game_funcs.py` (if it's a `RecompiledFuncs` patch — most
   likely, given the call originates inside `processSceneNode`) or directly
   in `lib/` runtime code if the unmasked add happens on the runtime side
   (check which repo the actual arithmetic lives in before choosing).

## Do not

- Do not re-attempt `otool`/`objdump` a 3rd time this session unless you
  have concrete new evidence the allowlist changed (e.g. check
  `.claude/settings.json` first) — confirmed blocked twice now (s193, s194).
- Do not touch `scratch/agent/s193_disasm.py` — still unvalidated, not
  needed now that the mcontext dump gives register-level ground truth for
  free.
- Do not re-touch the `[CRASH][siginfo]`/`[CRASH][mcontext]` dump itself —
  it's landed, confirmed working via positive control, and permanent
  (always-on, no env gate). Do not add an env gate to it.
- Do not re-touch `queueGPUUploadTMEM`'s guard or its s193 forcing hook —
  both closed and confirmed working.
- Do not re-touch the `processSceneNode` node-pointer guard (s190) — still
  intact, still 0/4 fires, still the primary untested target question.
- Do not write the s194 crash mechanism into CURRENT-TRUTH as a confirmed
  root cause on the strength of one occurrence — single-source, needs a
  2nd independent line of evidence first (iron rule 4).
- Do not attempt to root-cause `queueGPUUploadTMEM`'s actual corrupted-
  width/height source (goal-stack M3) — out of scope.
- Do not re-attempt root-causing the underlying `rs_free` free-list
  corruption source itself (s85-s114 chase) — still out of scope.
- Do not turn on `ROGUESQ_LOG_THREAD_RESUME=1` (s93's confound).

## Blocking on a long-running soak (learned the hard way, still current)

Run the driver script as a single foreground Bash call with output
redirected to a log file and a generous timeout (~480s), OR launch with
`run_in_background: true` and block on the returned task ID via
`TaskOutput(task_id, block=true, timeout=300000-480000)` — this is the
correct way to synchronously wait for a soak before writing the exit-
contract docs; ending the turn while a background soak is still running
trips the Stop hook's exit-contract check prematurely.

## This session's environment notes (carry forward, still current)

- **Disassembly tools (`nm`, `otool`, `lldb`, `objdump`) are NOT on the
  Bash allowlist** — confirmed a 2nd time this session (both `otool -tv -p`
  and `objdump --disassemble-symbols=` triggered approval prompts a
  non-interactive session can't clear). Stop trying at the start of a
  session if still blocked; the mcontext-dump workaround below now covers
  most of what disassembly would have been needed for anyway.
- **The crash handler now dumps siginfo + full ARM64 register file on every
  SIGSEGV/SIGBUS/SIGABRT** (`src/main/main.cpp`, `[CRASH][siginfo]`/
  `[CRASH][mcontext]` lines) — this is a durable capability for ALL future
  crash investigations, not just this one. Check for these lines first in
  any new crash log before reaching for a disassembler.
- `<ucontext.h>` errors ("_XOPEN_SOURCE required") on this SDK for the
  deprecated ucontext *functions*; `<sys/ucontext.h>` gives the same
  `ucontext_t`/`mcontext_t` *types* without that guard — use the latter.
- `scratch/agent/machoparse.py` gives symbol addr/size only (no
  disassembly) — reliable if ever needed again.
- `N64Recomp/fixup_game_funcs.py` is non-idempotent — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. If adding a NEW patch: regenerate fresh first (`zsh
  tools/agent/regen_n64recomp.sh`), THEN run `python3
  /absolute/path/to/N64Recomp/fixup_game_funcs.py > log` exactly once. Grep
  the log for the new patch's report line to confirm exactly x1, and check
  older patches' lines are ALSO x1 (not x2).
- A pure `lib/N64ModernRuntime`/`lib/rt64`/`src/main` runtime change (not a
  `RecompiledFuncs/*.c` patch) does NOT need the regen/fixup pipeline at
  all — just `cmake --build build --target RogueSquadron64Recomp -j`
  directly. (This is what s192's, s193's, AND s194's changes used.) A
  `processSceneNode` guard WOULD need the regen/fixup pipeline (it's a
  `RecompiledFuncs` patch).
- Re-running the same soak script/tag **overwrites** the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied — use
  absolute paths, no `cd`, one command per Bash call (including a trailing
  `echo` after a redirected command, and `cmd &` backgrounding — use the
  `run_in_background` tool parameter instead of shell `&`).
- `git -C <path> ...` AND `cd <path> && git ...` (combined in one Bash call)
  both trigger approval prompts that a non-interactive session can't clear
  — confirmed again this session for the `lib/N64ModernRuntime`/`lib/rt64`
  submodule dirty-state check. The `m lib/...` in top-level `git status` is
  a standing, permanent state from the applied `submodule-patches/*.patch`
  files, not something to "fix" — only run `export.sh` when YOU add a new
  edit under `lib/` in the same session.
- `submodule-patches/export.sh` must be invoked as
  `./submodule-patches/export.sh` (relative) from the repo root — absolute
  path gets denied.
- A large `run.log` (millions of lines) is fine to `grep -c`/`grep -n >
  outfile` directly — just don't `cat`/`Read` it wholesale.
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- Output redirection is sandboxed to the session's allowed working
  directories (this repo, N64Recomp, rogue_squadron64) — redirecting to
  `/tmp/...` gets blocked; use a path under `scratch/agent/` instead.
- Heredocs (`cat << 'EOF' > file`) get rejected as unparseable shell syntax
  by this session's Bash tool — use the Write tool to create files instead.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now ~270+ KB (`wc -l` ~3950+ lines) — WAY over
the ~35 KB CLAUDE.md budget, growing every session. Migrate durable
mechanism/architecture material to PROJECT-OVERVIEW.md and prune superseded
detail, paired with a real experiment. Flagged for many sessions without
action.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session. Still flagged
for the user, not committed autonomously.
