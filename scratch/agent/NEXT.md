# NEXT work unit (s1917)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

**Primary path — resume the sweep.** s1916 synchronized
`func_800F5D34` → `buildSineWaveEffectGeometryA` (TOML size
`0xC20` already matched generated `rom_size`; no bump). Do not
re-run `s790_postsec2_reachability.sh` without a new measurement
axis. Ask (b) (disposable clone + `git submodule update` bisect)
is still human-only.

Next leftover: `func_800F6954` at `0x800F6954` (TOML size `0x7DC`,
`syms/rogue_squadron.syms.toml:2010`). Already confirmed in
s1906–s1916 via the full four-step procedure:
1. Adjacency: `funcs_41.c:15028` (`buildSineWaveEffectGeometryA`)
   and `:17961` (`buildSineWaveEffectGeometryB`) are the only two
   `RECOMP_FUNC` lines matched — true adjacency.
2. `funcs.h:2168-2169` declares `buildSineWaveEffectGeometryA`
   then `buildSineWaveEffectGeometryB` in that exact order.
3. `recomp_overlays.inl:1897`: `buildSineWaveEffectGeometryB`
   offset is `0x00051824` = `buildSineWaveEffectGeometryA`'s
   `0x00050C04 + 0xC20` (its TOML size); `rom_size = 0x000007DC`
   matches the TOML's `size = 0x7DC` exactly.
4. `grep -rln 'func_800F6954'` across N64Recomp's `RecompiledFuncs/`
   tree: zero hits — non-collision.

Generated body matches the name: stack `-0x60`, same
`s1=$a0` / `s2=$a1` / `s0=$a3` / `f24=$a2` prologue as A,
then `lwc1 $f20, 0x8($s0)` and `jal 0x8001C400` (`sinfApprox`).
Companion `mission_overlay.txt` already names
`buildSineWaveEffectGeometryB = 0x800F6954`.
No existing TOML entry already uses `buildSineWaveEffectGeometryB`.
Sizes already agree — no bump.

All four already agree — this iteration can rename `func_800F6954`
to `buildSineWaveEffectGeometryB` directly (TOML metadata-only
sync, no build/regen needed), then re-verify + preview the one
after it the same way before stopping (matching the s1887-s1916
pattern).

Competing hypotheses for that leftover (already split):
- H1: leftover is `buildSineWaveEffectGeometryB` — SELECTED by
  the four-step table + companion + generated prologue.
- H2: offset/size/body disagree with the companion name —
  would require a TOML bump or skip.
- H3: the human name is already claimed by another TOML entry —
  collision; do not rename.

**After that leftover:** `func_800F7130` already lines up with
`renderNpcAnchoredProceduralEffect` (s1906–s1916 preview:
`funcs_41.c:17961,19845` / next is `funcs_42.c:35`,
`funcs.h:2169-2170`, `.inl:1898` offset `0x00052000 =
0x00051824 + 0x7DC` / `rom_size 0xB44`, zero-hit
`func_800F7130`). Companion already names
`renderNpcAnchoredProceduralEffect = 0x800F7130`. Body
matches: stack `-0x1B0`, `lhu $a0, 0x198($a0)` then
`jal 0x8004015C` (`getNpcContextField8`),
`t0=actor+0x8`, `s1=actor+0x50`. After that:
`func_800F7C74` lines up with `spawnAndUpdateEffectActors`
(`funcs_41.c:19845` then `funcs_42.c:35,1481`,
`funcs.h:2170-2171`, `.inl:1899` offset `0x00052B44 =
0x00052000 + 0xB44` / `rom_size 0x724`, zero-hit
`func_800F7C74`). Companion already names
`spawnAndUpdateEffectActors = 0x800F7C74`. Body matches:
stack `-0xC8`, `s2=0`, `s3=s2`, `$a1=8`. After that:
`func_800F8398` lines up with `executeActorType4Effect`
(`funcs_42.c:35,1481`, `funcs.h:2171-2172`, `.inl:1900`
offset `0x00053268 = 0x00052B44 + 0x724` / `rom_size 0x10DC`,
zero-hit `func_800F8398`). Companion already names
`executeActorType4Effect = 0x800F8398`. Body matches:
stack `-0x118`, `s7=$a0`, `s4=actor+0x8`,
`lhu $a0, 0x198($s7)` then `jal 0x8004015C`
(`getNpcContextField8`), `s6=actor+0x50`.

**Where the generated tree actually lives:** it is gitignored
(`RecompiledFuncs/` in `.gitignore`) and does NOT exist under this
repo's `build/` right now. It lives at
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/` (an
additional working directory) — `funcs_41.c`, `funcs_42.c`, `funcs.h`,
and `recomp_overlays.inl` are all there. Check there first; don't
re-search the whole filesystem.

**Before starting**, re-check the sweep's 15-title REVISIT gate:
`grep -n '^## Session ' PORTING-STATE.md | tail -15`. If all 15 titles
belong to the sweep (contain "synchronized" or "confirmed ... symbol"),
this iteration is a REVISIT instead — spend it re-attempting the
external retail-entry boundary or M4 accumulator-origin threads with a
genuinely new angle. As of s1916 this gate does NOT fire (s1902 is
still in the window — 1 of 15 slots non-sweep). s1917 starts with
s1902–s1916 still containing s1902. The window starts dropping s1902
only after s1917, so s1918 would be the first REVISIT if s1917 is
another sweep step.

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
