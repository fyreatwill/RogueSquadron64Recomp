# NEXT work unit (s2021)

HYPOTHESIS-ID: m5-service-direct-entry-caller-witness

## RESUME: where s2019/s2020 left off

s2019 exported a `get_function` witness to `submodule-patches/N64ModernRuntime.patch`.
That witness refuted the indirect-dispatch lookup as the phase-valid service
mechanism (both controls zero, phase gate live). s2020 is a checkpoint that
formally named the discrimination. No code for the direct-entry arm was written.
s2021 must add the direct-entry witness to `fixup_game_funcs.py` and run one
phase-valid port capture.

The retail oracle was already run in s2019: whole-RDRAM write control hit the
10,000-callback cap; `0x8009B5A8` executed 4,223 times; aggregate retail
predecessor was `0x80019B74`. A fresh oracle run is NOT required unless the
binary changed. The port binary at `build/RogueSquadron64Recomp` was last built
with the s2019 `get_function` witness but has NO direct-entry rows yet.

## Work unit

Add a bounded pre-phase entry control and a phase-gated direct entry/exit
witness to `serviceVoicePoolFrame` in `../N64Recomp/fixup_game_funcs.py`.
Do NOT modify `overlays.cpp` or the N64ModernRuntime patch — the direct-entry
probe belongs in the generated body via the fixup script.

The existing diagnostic tag is `[s2006-svc]` (unconditional pre-phase rows,
first 20 only). Add a second block:
- Tag `[s2020-svc]` (choose a tag name not already present in the log)
- Pre-phase bounded control: fire on the first N (e.g. 10) calls before
  `rs64_phase_ord() >= 4`, confirming the function is reachable before the
  phase gate
- Phase-gated entry row: fire on every call where `rs64_phase_ord() >= 4`,
  recording `rs64_phase_ord()`, the guest thread ID (if available), `ctx->r31`
  as derived call site, and the status byte at the standard slot-0 address
- Exit row: fire on return from the same phase-gated calls
- `0x8009B7EC` store edge: already in the existing diagnostic — keep it; do
  not add a new tag for it

After the fixup script change, regenerate in the required order:

```sh
cd /Users/williambuckley/Documents/Tools/N64Recomp
python tools/make_elf.py rogue_squadron.toml
build/Debug/N64Recomp.exe rogue_squadron.toml
python fixup_game_funcs.py
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run one phase-valid port capture (same recipe as s2019's successful specific arm):

```sh
env ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2021-direct-entry 30 12
```

Extract the discriminating rows:

```sh
RUN=scratch/s73_post_a_scene/s2021-direct-entry/run.log
rg -n -e '\[s2020-svc\]' -e '\[s2006-svc\]' -e '\[service-voice-pool-frame\]' -e '\[pcm-sanity\]' -e 'musyx-gate|audio-drain|\[phase\]' "$RUN" | tail -220
```

## Competing hypotheses and discriminator

- D1: Phase-valid `[s2020-svc]` entry fires AND pre-phase control fires → live
  direct service path. Move to writer/thread join (Next step #2 in CURRENT-TRUTH).
  Retail predecessor `0x80019B74` is the expected `ctx->r31 - 8` target.
- D2: Pre-phase control fires but phase-gated entry is zero → gate or missing
  caller before the function. Requires tracing the audio scheduler path.
- D3: Phase-valid entry fires with call site differing from retail `0x80019B74`
  → port call-path or scheduler mismatch; not a registration defect.
- D4: Entry fires but exit or `0x8009B7EC` store is absent → service-body or
  callback boundary; do not collapse into D2.

The discriminating table: pre-phase entry control count, phase-valid entry
count/call site/thread, phase-valid exit count, `0x8009B7EC` store count,
audio-gate/task rows, VI 1024 and 512 phase rows. Interpret only when the
pre-phase control is nonzero in the same run.
