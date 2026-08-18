# NEXT work unit (s1915)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

**Primary path — resume the sweep.** s1914 synchronized
`func_800F538C` → `executeActorType3Effect` (TOML size
`0x6A4` already matched generated `rom_size`; no bump). Do not
re-run `s790_postsec2_reachability.sh` without a new measurement
axis. Ask (b) (disposable clone + `git submodule update` bisect)
is still human-only.

Next leftover: `func_800F5A30` at `0x800F5A30` (TOML size `0x304`,
`syms/rogue_squadron.syms.toml:2008`). Already confirmed in
s1906–s1914 via the full four-step procedure:
1. Adjacency: `funcs_41.c:12993` (`executeActorType3Effect`)
   and `:14424` (`initActorAsType4`) are the only two
   `RECOMP_FUNC` lines matched — true adjacency.
2. `funcs.h:2166-2167` declares `executeActorType3Effect`
   then `initActorAsType4` in that exact order.
3. `recomp_overlays.inl:1895`: `initActorAsType4`
   offset is `0x00050900` = `executeActorType3Effect`'s
   `0x0005025C + 0x6A4` (its TOML size); `rom_size = 0x00000304`
   matches the TOML's `size = 0x304` exactly.
4. `grep -rln 'func_800F5A30'` across N64Recomp's `RecompiledFuncs/`
   tree: zero hits — non-collision.

Generated body matches the name: stack `-0x30`,
`sb $v0, 0x112($s1)` with `$v0=4`, then if assetName+0x0
non-null `jal 0x80047B48` (`getLevelDatItemByName`),
`s2=actor+0x50`. Companion `mission_overlay.txt`
already names `initActorAsType4 = 0x800F5A30`.
No existing TOML entry already uses `initActorAsType4`.
Sizes already agree — no bump.

All four already agree — this iteration can rename `func_800F5A30`
to `initActorAsType4` directly (TOML metadata-only
sync, no build/regen needed), then re-verify + preview the one
after it the same way before stopping (matching the s1887-s1914
pattern).

**After that leftover:** `func_800F5D34` already lines up with
`buildSineWaveEffectGeometryA` (s1906–s1914 preview:
`funcs_41.c:14424,15028`, `funcs.h:2167-2168`, `.inl:1896`
offset `0x00050C04 = 0x00050900 + 0x304` / `rom_size 0xC20`,
zero-hit `func_800F5D34`; body stack `-0x60`,
`s1=$a0`, `s2=$a1`, `s0=$a3`, `f24=$a2`,
reads `+0x8($s0)`). Companion already names
`buildSineWaveEffectGeometryA = 0x800F5D34`. After that:
`func_800F6954` lines up with `buildSineWaveEffectGeometryB`
(`funcs_41.c:15028,17961`, `funcs.h:2168-2169`, `.inl:1897`
offset `0x00051824 = 0x00050C04 + 0xC20` / `rom_size 0x7DC`,
zero-hit `func_800F6954`). Companion already names
`buildSineWaveEffectGeometryB = 0x800F6954`. Body matches:
stack `-0x60`, same `s1=$a0` / `s2=$a1` / `s0=$a3` /
`f24=$a2` prologue as A. After that: `func_800F7130` lines
up with `renderNpcAnchoredProceduralEffect`
(`funcs_41.c:17961` then `funcs_41.c:19845` /
`funcs_42.c:35` file-boundary next,
`funcs.h:2169-2170`, `.inl:1898` offset `0x00052000 =
0x00051824 + 0x7DC` / `rom_size 0xB44`, zero-hit
`func_800F7130`). Companion already names
`renderNpcAnchoredProceduralEffect = 0x800F7130`. Body
matches: stack `-0x1B0`, `lhu $a0, 0x198($a0)` then
`jal 0x8004015C` (`getNpcContextField8`),
`t0=actor+0x8`, `s1=actor+0x50`.

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
genuinely new angle. As of s1914 this gate does NOT fire (s1902 is
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
