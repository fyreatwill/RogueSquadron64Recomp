# NEXT work unit (s1903)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

**Primary path — resume the sweep.** s1902 closed H3a-lowpower (LPM-off
A/B: same `640 origin=0x00696100` stall, 0 VI 1024). Do not re-run
`s790_postsec2_reachability.sh` without a new measurement axis. Ask (b)
(disposable clone + `git submodule update` bisect) is still human-only.

Next leftover: `func_800F2FC0` at `0x800F2FC0` (size `0xC`,
`syms/rogue_squadron.syms.toml:1996`). Already confirmed in s1901 via
the full four-step procedure:
1. Adjacency: `funcs_41.c:5478` (`getEffectIntensity`) and `:5490`
   (`setEffectIntensity`) are the only two `RECOMP_FUNC` lines matched —
   true adjacency.
2. `funcs.h:2154-2155` declares `getEffectIntensity` then
   `setEffectIntensity` in that exact order.
3. `recomp_overlays.inl:1883`: `setEffectIntensity` offset is `0x0004DE90`
   = `getEffectIntensity`'s `0x0004DE84 + 0xC` (its TOML size);
   `rom_size = 0x0000000C` matches the TOML's `size = 0xC` for
   `func_800F2FC0` exactly.
4. `grep -rln 'func_800F2FC0\b'` across N64Recomp's `RecompiledFuncs/`
   tree: zero hits — non-collision.

Generated body also matches the name: `0x800F2FC0` is `sw $a1, 0x14C($a0)`
(same field `getEffectIntensity` loads via `lwc1 $f0, 0x14C($a0)`).

All four already agree — this iteration can rename `func_800F2FC0` to
`setEffectIntensity` directly (TOML metadata-only sync, no build/regen
needed), then re-verify + preview the one after it the same way before
stopping (matching the s1887-s1901 pattern).

**Bonus — the generated tree still runs ahead here.** After
`setEffectIntensity`, `recomp_overlays.inl:1884-1885` already shows two
more resolved names: `triggerCueWithSlotEffect` (offset `0x0004DE9C`,
size `0xE0`) and `copyPipeDelimitedField` (offset `0x0004DF7C`, size
`0x98`). Each still needs its own four-step confirmation (adjacency in
`funcs_41.c`, `funcs.h` order, `.inl` offset/size math, non-collision
grep) before renaming — do not skip the checks just because the `.inl`
name is already visible — but expect a couple more fast metadata-only
syncs before hitting the next genuinely-unresolved placeholder.

**Where the generated tree actually lives:** it is gitignored
(`RecompiledFuncs/` in `.gitignore`) and does NOT exist under this repo's
`build/` right now. It lives at
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/` (an
additional working directory) — `funcs_41.c`, `funcs.h`, and
`recomp_overlays.inl` are all there. Check there first; don't re-search the
whole filesystem.

**Before starting**, re-check the sweep's 15-title REVISIT gate:
`grep -n '^## Session ' PORTING-STATE.md | tail -15`. If all 15 titles
belong to the sweep (contain "synchronized" or "confirmed ... symbol"),
this iteration is a REVISIT instead — spend it re-attempting the external
retail-entry boundary or M4 accumulator-origin threads with a genuinely
new angle. As of s1902 this gate does NOT fire (s1888-s1892 plus s1902
are in the window — 6 of 15 slots non-sweep). The window starts dropping
s1888 only after s1903.

H3a-lowpower is closed. Do **not** re-check `thermal_probe.py` as a
reason to re-run the reachability recipe — that A/B is done.

## Do not repeat

- The s844-HEAD full code-content audit (s1890) — closed, no candidate
  found beyond `rs64_is_hangar_vi()`, already refuted.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed, refuted.
- H3a-lowpower (s1902) — closed, refuted. A same-recipe
  `s790_postsec2_reachability.sh` run with no new measurement axis is
  now 16 confirmations of the 640 `0x00696100` stall (10 of them on
  this regression, 1 of those with LPM confirmed off).
- Ask (b) from s1891 (disposable clone + `git submodule update` bisect at
  `ef7a0fb9`) is still open and still legitimately human-only per CLAUDE.md's
  hard rule — do not attempt a workaround.
