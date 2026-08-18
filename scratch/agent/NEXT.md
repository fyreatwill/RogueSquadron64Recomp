# NEXT work unit (s1890)

HYPOTHESIS-ID: vi1024-reachability-regression

This is the 4th iteration on this slug if opened again. s1888 and s1889
established and characterized the regression (8/8 fresh runs fail to reach
VI 1024, 4 crash/stall signatures, H1-flake refuted). s1890 did an
exhaustive audit and one built-and-refuted hypothesis; both counted
ADVANCED. **Do not repeat either.**

## What s1890 already closed — do NOT re-check

- **Full content audit of every non-ledger file that changed between s844
  (`ef7a0fb9`) and HEAD (1092 commits)**, not just a file-touch list:
  `submodule-patches/rt64.patch` and `N64ModernRuntime.patch` (372 combined
  lines) have exactly one line near any of the four crash signatures'
  symbols (`copyToRAM`, `clearDepthTarget`, `checkActiveRenderEncoder`,
  `beginRenderPass`, `fullSync`, `musyxRenderVoiceSamples`,
  `fillSampleStreamRange`, `musyxSynthFrame`, `viRetraceHandlerThread`) —
  an inert log-format-string edit. `tools/fixup_factor5_ucode.py`'s three
  new probe insertions are confirmed env-var-gated no-ops, and none of
  their vars are armed by `s790_postsec2_reachability.sh`. The freelist
  multi-header restore toggle predates s844 by 3 days. 1612 lines of
  `syms/rogue_squadron.syms.toml` changes are vram/size-identical renames
  (sampled and confirmed). **Do not re-audit this range; it is closed.**
- **H5-hangar-probe-race: BUILT and REFUTED.** `rs64_is_hangar_vi()` (added
  post-s844, called unconditionally every `M_GFXTASK` from the render
  thread, reads shared VI regs without visible locking) was gated behind a
  new `ROGUESQ_SKIP_HANGAR_PROBE` env var (see `docs/ENV-KNOBS.md`), the
  binary rebuilt once, and both arms run on the unmodified soak script:
  identical `640 origin=0x00696100` stall at 7.3-7.4s in both, only the
  crash-vs-timeout outcome differed (both already-catalogued signatures).
  **Do not rebuild or re-test this knob as if it were still open.**
- Stale/corrupted save state: `build/saves/rs64.n64.us.1.0.bin{,.bak}` dated
  2026-08-11, untouched by any run since. Not the cause.
- Disk space: data volume 95% used, 52 GiB free — not critical, not
  re-checked further.

## What's still open

- **H3-machine-state**: `uptime` (load 4.11/3.92/4.53 on 15 cores, ~27%
  avg) and `ps aux` (no other game process) went through in s1890 and show
  nothing alarming — but `top`, `vm_stat`, `who`, `pmset -g therm`,
  `sysctl` are ALL blocked by this session's permission policy, confirmed
  in both s1889 and s1890 (not a one-off). This does not cover machine
  state during the actual failing runs. **This needs a human to run one
  snapshot from outside the harness and paste it back** — that is the
  single highest-value remaining cheap action.
- **Historical-commit bisect**: cannot run under current tooling.
  `git submodule update` (needed to populate submodule content at a
  historical commit, even inside a fresh `git worktree`) is denied in
  `.claude/settings.json` by command-string match regardless of working
  directory. Sidestepping via `git -C lib/X checkout <hash>` would discard
  lib/'s uncommitted standing patches — the exact thing the deny rule
  protects — so do not attempt it. **This needs a human to run
  `git submodule update` once inside a disposable `git clone` elsewhere**
  (not this worktree), after which a future iteration can build and test a
  pre-s844 commit for comparison.
- H4-real-regression (the project's long-tracked freelist/heap-corruption
  family surfacing earlier) is the leading hypothesis by elimination, but
  still has no established mechanism — `fl-zero-watch` caught corruption in
  2/3 of s1889's runs, single-source, no positive control (no successful
  1024 reach exists since s844 to check the watch against).

## Recommended next iteration

If a human has supplied either the system snapshot or run
`git submodule update` in a scratch clone: act on it (deeper H3 read, or
the actual bisect). If neither has happened: **write
`scratch/agent/BLOCKED.md`** naming both asks explicitly and go BLOCKED —
do not spend a 4th consecutive iteration re-confirming "still stalls at
640/0x00696100." A clean, well-audited stall is not new information the
5th time.

## Exact commands (for the bisect once unblocked, or a fresh soak)

```
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
zsh scratch/agent/s790_postsec2_reachability.sh   # repeat as needed
grep -a '\[phase\] vi_width=1024' <outdir>/run.log       # presence = reached
grep -a 'fl-zero-poll' <outdir>/run.log | grep -av 'fault_n=0 '  # corruption lead
```
