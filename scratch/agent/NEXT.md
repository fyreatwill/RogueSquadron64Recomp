# NEXT work unit (s1910)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

**Primary path — resume the sweep.** s1909 synchronized
`func_800F3290` → `resolveScriptedNameTokenList` (TOML size
`0x24C` already matched generated `rom_size`; no bump). Do not
re-run `s790_postsec2_reachability.sh` without a new measurement
axis. Ask (b) (disposable clone + `git submodule update` bisect)
is still human-only.

Next leftover: `func_800F34DC` at `0x800F34DC` (TOML size `0x7D4`,
`syms/rogue_squadron.syms.toml:2003`). Already confirmed in
s1906–s1909 via the full four-step procedure:
1. Adjacency: `funcs_41.c:6092` (`resolveScriptedNameTokenList`)
   and `:6547` (`computeRandomizedOrientationFrame`) are the only
   two `RECOMP_FUNC` lines matched — true adjacency.
2. `funcs.h:2161-2162` declares `resolveScriptedNameTokenList`
   then `computeRandomizedOrientationFrame` in that exact order.
3. `recomp_overlays.inl:1890`: `computeRandomizedOrientationFrame`
   offset is `0x0004E3AC` = `resolveScriptedNameTokenList`'s
   `0x0004E160 + 0x24C` (its TOML size); `rom_size = 0x000007D4`
   matches the TOML's `size = 0x7D4` exactly.
4. `grep -rln 'func_800F34DC'` across N64Recomp's `RecompiledFuncs/`
   tree: zero hits — non-collision.

Generated body matches the name: calls `rand` (`jal 0x80003430`)
three times (`0x800F3654`, `0x800F37D4`, `0x800F380C`), plus
`cosf` (`jal 0x8002B190`) and `normalize_vector`
(`jal 0x8001CF58`), after reading the orientation triplet at
`+0x60/+0x64/+0x68`. Companion `mission_overlay.txt` already names
`computeRandomizedOrientationFrame = 0x800F34DC`. No existing
TOML entry already uses `computeRandomizedOrientationFrame`.
Sizes already agree — no bump.

All four already agree — this iteration can rename `func_800F34DC`
to `computeRandomizedOrientationFrame` directly (TOML metadata-only
sync, no build/regen needed), then re-verify + preview the one
after it the same way before stopping (matching the s1887-s1909
pattern).

**After that leftover:** `func_800F3CB0` already lines up with
`updateNpcEffectIntensity` (s1906–s1909 preview:
`funcs_41.c:6547,8302`, `funcs.h:2162-2163`, `.inl:1891` offset
`0x0004EB80 = 0x0004E3AC + 0x7D4` / `rom_size 0x45C`, zero-hit
`func_800F3CB0`; body `jal 0x800F2FC0` → `setEffectIntensity`).
After that: `func_800F410C` lines up with
`executeActorType1Effect` (`funcs_41.c:8302,9212`,
`funcs.h:2163-2164`, `.inl:1892` offset `0x0004EFDC =
0x0004EB80 + 0x45C` / `rom_size 0xD68`, zero-hit
`func_800F410C`).

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
genuinely new angle. As of s1909 this gate does NOT fire (s1902 is
still in the window — 1 of 15 slots non-sweep). The window starts
dropping s1902 only after s1917.

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
