# NEXT work unit (s1911)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

**Primary path — resume the sweep.** s1910 synchronized
`func_800F34DC` → `computeRandomizedOrientationFrame` (TOML size
`0x7D4` already matched generated `rom_size`; no bump). Do not
re-run `s790_postsec2_reachability.sh` without a new measurement
axis. Ask (b) (disposable clone + `git submodule update` bisect)
is still human-only.

Next leftover: `func_800F3CB0` at `0x800F3CB0` (TOML size `0x45C`,
`syms/rogue_squadron.syms.toml:2004`). Already confirmed in
s1906–s1910 via the full four-step procedure:
1. Adjacency: `funcs_41.c:6547` (`computeRandomizedOrientationFrame`)
   and `:8302` (`updateNpcEffectIntensity`) are the only two
   `RECOMP_FUNC` lines matched — true adjacency.
2. `funcs.h:2162-2163` declares `computeRandomizedOrientationFrame`
   then `updateNpcEffectIntensity` in that exact order.
3. `recomp_overlays.inl:1891`: `updateNpcEffectIntensity`
   offset is `0x0004EB80` = `computeRandomizedOrientationFrame`'s
   `0x0004E3AC + 0x7D4` (its TOML size); `rom_size = 0x0000045C`
   matches the TOML's `size = 0x45C` exactly.
4. `grep -rln 'func_800F3CB0'` across N64Recomp's `RecompiledFuncs/`
   tree: zero hits — non-collision.

Generated body matches the name: calls `setEffectIntensity`
(`jal 0x800F2FC0` at `0x800F3F40`). Companion `mission_overlay.txt`
already names `updateNpcEffectIntensity = 0x800F3CB0`. No existing
TOML entry already uses `updateNpcEffectIntensity`. Sizes already
agree — no bump.

All four already agree — this iteration can rename `func_800F3CB0`
to `updateNpcEffectIntensity` directly (TOML metadata-only
sync, no build/regen needed), then re-verify + preview the one
after it the same way before stopping (matching the s1887-s1910
pattern).

**After that leftover:** `func_800F410C` already lines up with
`executeActorType1Effect` (s1906–s1910 preview:
`funcs_41.c:8302,9212`, `funcs.h:2163-2164`, `.inl:1892` offset
`0x0004EFDC = 0x0004EB80 + 0x45C` / `rom_size 0xD68`, zero-hit
`func_800F410C`; body reads actor+0x198 /
+0xD8/+0xDC/+0xE0 and intensity at +0x10C via `s5=actor+0x8`,
matching companion). After that: `func_800F4E74` lines up with
`executeActorType2Effect` (`funcs_41.c:9212,11890`,
`funcs.h:2164-2165`, `.inl:1893` offset `0x0004FD44 =
0x0004EFDC + 0xD68` / `rom_size 0x518`, zero-hit
`func_800F4E74`). Companion already names
`executeActorType2Effect = 0x800F4E74`.

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
genuinely new angle. As of s1910 this gate does NOT fire (s1902 is
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
