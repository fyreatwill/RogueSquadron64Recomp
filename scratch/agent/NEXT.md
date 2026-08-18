# NEXT work unit (s1912)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

**Primary path — resume the sweep.** s1911 synchronized
`func_800F3CB0` → `updateNpcEffectIntensity` (TOML size
`0x45C` already matched generated `rom_size`; no bump). Do not
re-run `s790_postsec2_reachability.sh` without a new measurement
axis. Ask (b) (disposable clone + `git submodule update` bisect)
is still human-only.

Next leftover: `func_800F410C` at `0x800F410C` (TOML size `0xD68`,
`syms/rogue_squadron.syms.toml:2005`). Already confirmed in
s1906–s1911 via the full four-step procedure:
1. Adjacency: `funcs_41.c:8302` (`updateNpcEffectIntensity`)
   and `:9212` (`executeActorType1Effect`) are the only two
   `RECOMP_FUNC` lines matched — true adjacency.
2. `funcs.h:2163-2164` declares `updateNpcEffectIntensity`
   then `executeActorType1Effect` in that exact order.
3. `recomp_overlays.inl:1892`: `executeActorType1Effect`
   offset is `0x0004EFDC` = `updateNpcEffectIntensity`'s
   `0x0004EB80 + 0x45C` (its TOML size); `rom_size = 0x00000D68`
   matches the TOML's `size = 0xD68` exactly.
4. `grep -rln 'func_800F410C'` across N64Recomp's `RecompiledFuncs/`
   tree: zero hits — non-collision.

Generated body matches the name: reads actor+0x198
(`lhu $a0, 0x198($s7)`), the position triplet at
+0xD8/+0xDC/+0xE0, and intensity at +0x10C via
`s5=actor+0x8` (`lwc1 $f0, 0x104($s5)`). Companion
`mission_overlay.txt` already names
`executeActorType1Effect = 0x800F410C`. No existing
TOML entry already uses `executeActorType1Effect`. Sizes
already agree — no bump.

All four already agree — this iteration can rename `func_800F410C`
to `executeActorType1Effect` directly (TOML metadata-only
sync, no build/regen needed), then re-verify + preview the one
after it the same way before stopping (matching the s1887-s1911
pattern).

**After that leftover:** `func_800F4E74` already lines up with
`executeActorType2Effect` (s1906–s1911 preview:
`funcs_41.c:9212,11890`, `funcs.h:2164-2165`, `.inl:1893` offset
`0x0004FD44 = 0x0004EFDC + 0xD68` / `rom_size 0x518`, zero-hit
`func_800F4E74`; body stack `-0x88`, reads actor+0x198 then
`getNpcContextField8` (`jal 0x8004015C`), `s2=actor+0x8`,
matching companion). After that: `func_800F538C` lines up with
`executeActorType3Effect` (`funcs_41.c:11890,12993`,
`funcs.h:2165-2166`, `.inl:1894` offset `0x0005025C =
0x0004FD44 + 0x518` / `rom_size 0x6A4`, zero-hit
`func_800F538C`). Companion already names
`executeActorType3Effect = 0x800F538C`. Body matches: stack
`-0x98`, same +0x198 NPC-context prologue.

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
genuinely new angle. As of s1911 this gate does NOT fire (s1902 is
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
