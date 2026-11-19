# Upstream comparison (2026-11-18)

Upstream = MikeSemicolonD/RogueSquadron64Recomp `main` (fetched here as `origin/main`, 603 commits since our
fork point 3cd3cb2b1). Done by an interactive owner session; findings below were read from upstream's code
and docs (CONFIRMED) unless marked PLAUSIBLE. Owner decision: port G6a rumble, G6b a rebinding tool that keeps
our defaults, G6c far-object stand-ins (tools/agent/ITERATION.md). Do not merge or cherry-pick upstream.

## Architecture differences

| Area | Ours | Upstream |
|---|---|---|
| Graphics | Factor 5 gfx ucode recompiled (RSPRecomp, LLE), RDP stream into RT64 (submodule-patches/rt64.patch) | Native F5 display-list parser in its RT64 fork (HLE, lib/rt64/src/gbi/rt64_gbi_f3dfactor5.cpp); gfx ucode not recompiled; new GPU terrain renderer on by default |
| Audio | MusyX ucode recompiled (src/rsp/aspMain.cpp) | Also recompiled (rsp/musyx_rsp.toml, src/audio/audio.cpp) |
| Patching generated code | Post-process C: tools/regen_replay.sh + ~485 tools/fixup_*/apply_s*.py | 371 `[[patches.hook]]` in rogue_squadron.toml -> src/game/toml_hooks.c, plus MIPS C in patches/; generated C never hand-edited |
| Platforms | macOS only, tested | Windows, Linux, Android, VR, macOS .app cross-built and never run on a Mac |
| Input | Hard-coded map in get_n64_input (main.cpp); rumble stub | src/input/: rebinding (roguesq_input.json, F6 panel), mouse flight, gyro, rumble, lightbar |
| Settings | ROGUESQ_* env vars, audio_device.txt | JSON configs + in-game menus |

Upstream features built on HLE + toml hooks (frame interpolation, terrain renderer / 8x draw distance, ray
tracing, in-game menus, mods, co-op) cannot be hosted by our LLE + fixup pipeline. Host-side pieces (input,
rumble, config) and the renderer-independent stand-ins can.

## Upstream on this Mac (native build test, 2026-11-18)

Builds natively in ~4 min (full Xcode needed for `metal`; ROM also needed in repo root for RSPRecomp; code mods
need setup.sh's extra step). Then fails at runtime, both macOS-specific:
1. SIGBUS in ModContext::resolve_code_dependencies: librecomp mods.cpp unprotect() uses mprotect on __TEXT
   (maxprot r-x on macOS); a `mach_vm_protect(..., VM_PROT_READ|VM_PROT_WRITE|VM_PROT_COPY)` branch fixes it.
2. Black screen: rs64::app::poll_input (src/input/input_host.cpp:977) pumps SDL/Cocoa events from the game's SI
   service thread; AppKit throws NSException off the main thread, killing the SI thread, so controller reads
   never complete. Fix needs event pumping moved to the main thread.

## Fix exchange candidates

- Upstream -> us: rumble (G6a), rebinding UI ideas (G6b), stand-ins for pop-in at dd>1 (G6c).
- Us -> upstream (PLAUSIBLE relevance): the two macOS bugs above; macOS display/fullscreen/Retina code
  (rs64_display_mac.mm); guest races we guard (allocateSongChannelArray voiceCount s147,
  evalCubicSplineAtTime divide s83, heap exhaustion at dd>1 via OSMEM 12) have no matching upstream hooks.
