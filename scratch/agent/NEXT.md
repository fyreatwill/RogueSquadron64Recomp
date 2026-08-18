# NEXT work unit (s1907)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

**Primary path — resume the sweep.** s1906 synchronized
`func_800F3144` → `copyRandomPipeDelimitedField`. Do not re-run
`s790_postsec2_reachability.sh` without a new measurement axis. Ask (b)
(disposable clone + `git submodule update` bisect) is still human-only.

Next leftover: `func_800F3258` at `0x800F3258` (size `0x8`,
`syms/rogue_squadron.syms.toml:2000`). Already confirmed in s1905 and
re-checked in s1906 via the full four-step procedure:
1. Adjacency: `funcs_41.c:5811` (`copyRandomPipeDelimitedField`) and
   `:6046` (`returnZero_800F3258`) are the only two `RECOMP_FUNC` lines
   matched — true adjacency.
2. `funcs.h:2158-2159` declares `copyRandomPipeDelimitedField` then
   `returnZero_800F3258` in that exact order.
3. `recomp_overlays.inl:1887`: `returnZero_800F3258` offset is
   `0x0004E128` = `copyRandomPipeDelimitedField`'s `0x0004E014 + 0x114`
   (its TOML size); `rom_size = 0x00000008` matches the TOML's
   `size = 0x8` for `func_800F3258` exactly.
4. `grep -rln 'func_800F3258'` across N64Recomp's `RecompiledFuncs/`
   tree: zero hits — non-collision.

Generated body also matches the name: `jr $ra` /
`addu $v0, $zero, $zero`.

All four already agree — this iteration can rename `func_800F3258` to
`returnZero_800F3258` directly (TOML metadata-only sync, no
build/regen needed), then re-verify + preview the one after it the
same way before stopping (matching the s1887-s1906 pattern).

**Later leftover, not this next rename:** `func_800F3260` TOML size
`0x2C` vs generated `tallyMidDetailObject` `rom_size 0x30`. The 4-byte
gap is the alignment nop at `0x800F328C`. Decide whether to bump the
TOML size when that leftover is reached; do not silently keep `0x2C`.
After that leftover: `func_800F3290` already lines up with
`resolveScriptedNameTokenList` (s1906 preview: `funcs_41.c:6056,6092`,
`funcs.h:2160-2161`, `.inl:1889` offset `0x0004E160 = 0x0004E130 +
0x30` / `rom_size 0x24C`, zero-hit `func_800F3290`).

**Where the generated tree actually lives:** it is gitignored
(`RecompiledFuncs/` in `.gitignore`) and does NOT exist under this
repo's `build/` right now. It lives at
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/` (an
additional working directory) — `funcs_41.c`, `funcs.h`, and
`recomp_overlays.inl` are all there. Check there first; don't re-search
the whole filesystem.

**Before starting**, re-check the sweep's 15-title REVISIT gate:
`grep -n '^## Session ' PORTING-STATE.md | tail -15`. If all 15 titles
belong to the sweep (contain "synchronized" or "confirmed ... symbol"),
this iteration is a REVISIT instead — spend it re-attempting the
external retail-entry boundary or M4 accumulator-origin threads with a
genuinely new angle. As of s1906 this gate does NOT fire (s1892 plus
s1902 are in the window — 2 of 15 slots non-sweep). The window starts
dropping s1892 only after s1907.

H3a-lowpower is closed. Do **not** re-check `thermal_probe.py` as a
reason to re-run the reachability recipe — that A/B is done.

## Do not repeat

- The s844-HEAD full code-content audit (s1890) — closed, no candidate
  found beyond `rs64_is_hangar_vi()`, already refuted.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed, refuted.
- H3a-lowpower (s1902) — closed, refuted. A same-recipe
  `s790_postsec2_reachability.sh` run with no new measurement axis is
  now 16 confirmations of the 640 `0x00696100` stall (10 of those on
  this regression, 1 of those with LPM confirmed off).
- Ask (b) from s1891 (disposable clone + `git submodule update` bisect
  at `ef7a0fb9`) is still open and still legitimately human-only per
  CLAUDE.md's hard rule — do not attempt a workaround.
