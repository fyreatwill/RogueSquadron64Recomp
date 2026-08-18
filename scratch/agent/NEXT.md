# NEXT work unit (s1905)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

**Primary path — resume the sweep.** s1904 synchronized
`func_800F2FCC` → `triggerCueWithSlotEffect`. Do not re-run
`s790_postsec2_reachability.sh` without a new measurement axis. Ask (b)
(disposable clone + `git submodule update` bisect) is still human-only.

Next leftover: `func_800F30AC` at `0x800F30AC` (size `0x98`,
`syms/rogue_squadron.syms.toml:1998`). Already confirmed in s1903 and
re-checked in s1904 via the full four-step procedure:
1. Adjacency: `funcs_41.c:5503` (`triggerCueWithSlotEffect`) and `:5668`
   (`copyPipeDelimitedField`) are the only two `RECOMP_FUNC` lines
   matched — true adjacency.
2. `funcs.h:2156-2157` declares `triggerCueWithSlotEffect` then
   `copyPipeDelimitedField` in that exact order.
3. `recomp_overlays.inl:1885`: `copyPipeDelimitedField` offset is
   `0x0004DF7C` = `triggerCueWithSlotEffect`'s `0x0004DE9C + 0xE0` (its
   TOML size); `rom_size = 0x00000098` matches the TOML's
   `size = 0x98` for `func_800F30AC` exactly.
4. `grep -rln 'func_800F30AC\b'` across N64Recomp's `RecompiledFuncs/`
   tree: zero hits — non-collision.

Generated body also matches the name: walks `$a0` until NUL, comparing
each byte to `0x7C` (`'|'`), copies the selected field into `$a2`.

All four already agree — this iteration can rename `func_800F30AC` to
`copyPipeDelimitedField` directly (TOML metadata-only sync, no
build/regen needed), then re-verify + preview the one after it the
same way before stopping (matching the s1887-s1904 pattern).

**Bonus — the generated tree still runs ahead here.** After
`copyPipeDelimitedField`, `recomp_overlays.inl:1886` already shows
`copyRandomPipeDelimitedField` (offset `0x0004E014`, size `0x114`).
s1904 already ran its four-step confirmation (`funcs_41.c:5668,5811`,
`funcs.h:2157-2158`, `.inl` offset/size math, non-collision on
`func_800F3144`) — still re-check before renaming, but expect another
fast metadata-only sync. Generated body jal's `rand_recomp` then
walks the same `|`-delimited field.

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
genuinely new angle. As of s1904 this gate does NOT fire (s1890-s1892
plus s1902 are in the window — 4 of 15 slots non-sweep). The window
starts dropping s1890 only after s1905.

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
