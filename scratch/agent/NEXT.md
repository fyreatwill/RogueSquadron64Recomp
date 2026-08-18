# NEXT work unit (s1908)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

**Primary path — resume the sweep.** s1907 synchronized
`func_800F3258` → `returnZero_800F3258`. Do not re-run
`s790_postsec2_reachability.sh` without a new measurement axis. Ask (b)
(disposable clone + `git submodule update` bisect) is still human-only.

Next leftover: `func_800F3260` at `0x800F3260` (TOML size `0x2C`,
`syms/rogue_squadron.syms.toml:2001`). Already confirmed in s1906 and
re-checked in s1907 via the full four-step procedure:
1. Adjacency: `funcs_41.c:6046` (`returnZero_800F3258`) and
   `:6056` (`tallyMidDetailObject`) are the only two `RECOMP_FUNC` lines
   matched — true adjacency.
2. `funcs.h:2159-2160` declares `returnZero_800F3258` then
   `tallyMidDetailObject` in that exact order.
3. `recomp_overlays.inl:1888`: `tallyMidDetailObject` offset is
   `0x0004E130` = `returnZero_800F3258`'s `0x0004E128 + 0x8`
   (its TOML size); `rom_size = 0x00000030` (not the TOML's `0x2C`).
4. `grep -rln 'func_800F3260'` across N64Recomp's `RecompiledFuncs/`
   tree: zero hits — non-collision.

Generated body matches the name: `lbu 0x15($a0)`, `srl 6`, compare
to 2, else increment the halfword at `0x80130B84`
(`0x80130B78+0xC`). Companion `mission_overlay.txt` already names
`tallyMidDetailObject = 0x800F3260` ("21 callers: (object_ptr) —
increments mid-detail object counter at 0x80130B84"). No existing
TOML entry already uses `tallyMidDetailObject`.

**Size decision (do not silently keep `0x2C`):** bump the TOML size
to `0x30` in the same rename. Competing readings:
- H-live-only: TOML `0x2C` is the live-insn span (`jr`/`nop` at
  `0x800F3284`/`0x800F3288`); keep it.
- H-include-pad: the generated overlay table, the offset chain to
  `resolveScriptedNameTokenList` (`0x0004E130 + 0x30 = 0x0004E160`),
  and the absence of any companion/generated/TOML occupant at
  `0x800F328C` all treat the alignment nop as part of this function.

H-include-pad is already selected by those three independent sources
(s1906 + s1907). Discriminator if re-opened: a `0x800F328C` leftover
or a generated `RECOMP_FUNC` starting there. None exists.

All four already agree — this iteration can rename `func_800F3260` to
`tallyMidDetailObject` directly (TOML metadata-only sync, no
build/regen needed), bumping `size` from `0x2C` to `0x30`, then
re-verify + preview the one after it the same way before stopping
(matching the s1887-s1907 pattern).

**After that leftover:** `func_800F3290` already lines up with
`resolveScriptedNameTokenList` (s1906/s1907 preview:
`funcs_41.c:6056,6092`, `funcs.h:2160-2161`, `.inl:1889` offset
`0x0004E160 = 0x0004E130 + 0x30` / `rom_size 0x24C`, zero-hit
`func_800F3290`). After that: `func_800F34DC` lines up with
`computeRandomizedOrientationFrame` (`funcs_41.c:6092,6547`,
`funcs.h:2161-2162`, `.inl:1890` offset `0x0004E3AC = 0x0004E160 +
0x24C` / `rom_size 0x7D4`, zero-hit `func_800F34DC`).

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
genuinely new angle. As of s1907 this gate does NOT fire (s1902 is
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
