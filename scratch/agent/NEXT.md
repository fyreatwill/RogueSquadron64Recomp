# NEXT work unit (s1918) — mandatory 15-title REVISIT

HYPOTHESIS-ID: vi1024-early-crash-not-stall

**This is a REVISIT, not a sweep step.** After s1917 the last 15
titles are s1903–s1917, every one a "synchronized the … symbol"
sweep title. Do **not** rename `func_800F7130`. Resume the sweep
at that leftover only in s1919 (HYPOTHESIS-ID back to
`generated-symbol-renaming-sweep`).

Do **not** re-run `s790_postsec2_reachability.sh`. That recipe is
closed without a new measurement axis (10/10, H3a-lowpower
refuted). Ask (b) (disposable clone + `git submodule update`
bisect at `ef7a0fb9`) is still human-only.

## Work unit — offline [phase] timeline table

s844 (last known VI-1024 success,
`scratch/agent/soak_results/s790_postsec2_reachability_20260813-061248/run.log`)
first hits `640 origin=0x00696100` at **11.0s** (`update_screen
#600`) and only then publishes `1024 origin=0x00790400` at
**79.6s**. s1902 first hits the **same** origin at **6.8s**
(`update_screen #359`) and has **no later [phase] line** before
the ~17s `findTileCopyId` SIGABRT. If current failures die 10–70s
into the same 640/`0x00696100` dwell that s844 sat in for ~68s,
the "stall at 640" framing is a misnomer and the regression is
an earlier crash, not a new VI-transition failure.

Competing hypotheses (discriminated by one offline table; no
build, no new game run):

- H1 early-crash-not-stall: every current failure first hits
  `640 origin=0x00696100` after the same preceding
  `320 → 640/0x0066A500` pair s844 used, then dies of a
  catalogued crash (copyToRAM / AGX `clearDepthTarget` / musyx
  SIGBUS / `findTileCopyId`) 10–70s later, still at that origin,
  before s844's ~68s 1024 transition. SELECTS: the 1024 "stall"
  is the crash family arriving earlier in a healthy dwell.
- H2 early-wrong-transition: current logs reach
  `0x00696100` by a different preceding origin/width sequence or
  a wildly different `update_screen` count than s844 — the 6.8s
  hit is a new, earlier, wrong VI change.
- H3 true-stall: at least one current log lives past 80s wall
  at `0x00696100` with no 1024 and no crash. SELECTS: a real
  stuck VI, not an early death.
- H4 log-incomparable: s844 `[phase]` format, origin set, or
  recipe env is not the same series as the 20260817 logs.

**Discriminating measurement** — one table, all existing logs,
no new run. For s844 plus every s1888/s1889/s1892/s1902
`s790_postsec2_reachability_*` log under
`scratch/agent/soak_results/`:

| col | how |
|---|---|
| first 320 time / us# / origin | `grep '\[phase\]' \| head` |
| first 640 / `0x0066A500` time / us# | same |
| first 640 / `0x00696100` time / us# | same |
| last `[phase]` time / width / origin | `grep '\[phase\]' \| tail -1` |
| last wall / crash signature | existing SOAK-RESULTS + `grep -E 'SIGSEGV\|SIGBUS\|SIGABRT\|last-guest-pc'` |
| 1024 present? | `grep -c 'vi_width=1024'` |

H1 needs: same preceding pair, 1024 count 0, last wall < 80s,
crash in the catalogued set, last `[phase]` still 640/`0x00696100`.
H2 needs: a different preceding origin or a first-`0x00696100`
`update_screen` not in the same neighborhood as s844's #600.
H3 needs: last wall ≥ 80s, 1024 count 0, process still in the
640 dwell.
H4 needs: missing `[phase]` lines or a different origin
vocabulary so the columns cannot be filled.

Same-run positive control: s844's own row must show 1024 at
~79.6s and the 11.0s `0x00696100` hit — if that row cannot be
reproduced from the file, the table is invalid.

Logs to include (do not add a new run):
- s844 success:
  `scratch/agent/soak_results/s790_postsec2_reachability_20260813-061248/run.log`
- 20260817 failures (s1888–s1902):
  `s790_postsec2_reachability_20260817-{173130,174630,174727,174818,180331,180706,181917,185603}`
  plus any sibling dirs from those sessions. Confirm the set
  with `ls scratch/agent/soak_results | grep 20260817`.

Do **not** treat a single s844-vs-s1902 pair as the result —
that pair is the prompt, not the table. All failure logs in
one comparison (iron rule 13).

## Sweep leftover (s1919, after this REVISIT)

`func_800F7130` → `renderNpcAnchoredProceduralEffect` (TOML
`0xB44` already matches generated `rom_size`; no bump).
Four-step already complete in s1906–s1917. After that:
`func_800F7C74` → `spawnAndUpdateEffectActors`;
`func_800F8398` → `executeActorType4Effect`;
`func_800F9474` → `clearObjectField112` (size `0x8`,
`sb $zero, 0x112($a0); jr $ra`, `.inl:1901` offset
`0x00054344 = 0x00053268 + 0x10DC`). Companion already
names all four. Generated tree lives at
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/`.

## Do not repeat

- The s844-HEAD full code-content audit (s1890) — closed.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed.
- H3a-lowpower (s1902) — closed. A same-recipe
  `s790_postsec2_reachability.sh` run with no new measurement
  axis is now 16 confirmations of the 640 `0x00696100` dwell
  (10 of those on this regression).
- Ask (b) from s1891 — still human-only.
- Another sweep rename this iteration — the 15-title gate
  forbids it.
