# NEXT work unit (s2164) — unsigned KSEG0 MEM_* census in cinematic SIGBUS sites

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2163 selected `H-CinematicRegress` and reverted A1 default-on.
Unset matched `=1` at dispatch/wait (`real_ucode=1`, wait return
`c=0x11`) but failed title at 640 `0x00696100`; same-build stub
retry reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`. Crash sites: `slotDispatcherIter+3092`
(`si_addr=0x37fff0019` = `rdram+0x7fff0019`) and
`cutsceneDispatchSlotsByFlag+8960` (`si_addr=0x380000044` =
`rdram+0x80000044`). Same unsigned-KSEG0 host-offset class as
s2161/s2162, different functions.

Grep-enumerate unsigned KSEG0 `MEM_BU`/`MEM_W`/`MEM_H` in those
two functions (and only those two). Classify every site: S32-address
like s2162, or prove dead / not KSEG0. Do not re-flip default-on,
add a wait/slot guard, or chase a single crash with a new skip.

Table from s2163: `scratch/s73_post_a_scene/s2163_default_on_ab.txt`.

## Competing hypotheses and discriminator

- `H-UnsignedKseg0Again`: one or more PATCH `MEM_*` in those
  functions uses an unsigned KSEG0 constant (e.g. `0x80000044` or
  `0x7fff0019`). S32-addressing is host addressing of a guest
  pointer, same ORIGIN shape as s2162. After the S32 change, a
  same-build `=1`/`=0` pair must reach title (and hangar if the
  recipe does).
- `H-NoSuchSite`: neither function contains unsigned KSEG0 `MEM_*`.
  The `si_addr` lead is refuted at source; do not S32-address by
  guess. Park and ask the oracle whether retail executes those PCs
  at VI 640 `0x00696100` and what pointer they load.
- `H-ImageTimingOnly`: sites exist but are also on the stub path
  (stub first-attempt also SIGBUS'd). S32-addressing still applies
  if the idiom is real; do not treat stub's first SIGBUS as proof
  the idiom is absent.
- `H-CoverageFailure`: the functions cannot be found in
  `RecompiledFuncs` / `fixup_game_funcs.py`. Null census is
  unevaluable.

Positive control: the grep must print the function definition line
and every `MEM_*` hit inside the body. A zero-hit claim requires
the definition line in the same output.

## Exact commands

Find the functions, then bound-grep `MEM_B`/`MEM_H`/`MEM_W` with
`0x8`/`0x7fff` constants. If S32-addressing, also edit
`../N64Recomp/fixup_game_funcs.py` (regen-safe) as s2162 did.

    grep -n '^void slotDispatcherIter\|^void cutsceneDispatchSlotsByFlag' \
      ../N64Recomp/RecompiledFuncs/funcs_*.c

If sites are S32-addressed, one Debug rebuild and a same-build
`=1`/`=0` title/hangar pair:

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
      cmake --build build --target RogueSquadron64Recomp -j 8

    env GAME_EXTRA_ENV="ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_AUDIO_UCODE=1" \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2164_image 30 12

    env GAME_EXTRA_ENV="ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_AUDIO_UCODE=0" \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2164_stub 30 12

If no sites, do not rebuild; write the empty-census table and stop.
Do not flip `get_rsp_microcode`. If an arm SIGSEGVs/SIGBUS at the
same cinematic window after S32, do not add a guard this iteration.
