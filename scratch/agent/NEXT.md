# NEXT work unit (s2217) — reconcile retail audio gate and task boundaries

HYPOTHESIS-ID: m5-audio-ground-truth-reconciliation

## Work unit

Execute step 1 of `docs/M5-AUDIO-PLAN.md` only. Run the Rice-driven retail
oracle first, with the whole-RDRAM positive control before the physical watches
for the MusyX gate (`0xA0F50`), audio countdown/status words (`0x14998A` and
`0x14974C`), and the known audio-task/AI callsites. Then run one existing port
boot/title route with the passive M5 diagnostics and silent-audio control. Do
not edit generated code, change a gate, enable the image arm, or build in this
unit.

Competing hypotheses and the single discriminator:

- H-RetailGateWriters: retail writes `0xA0F50` from the named init/display
  PCs with a legitimate zero-to-one transition; the port's existing
  `[m5-gate]` rows show the same value contract and downstream task/slot
  activity.
- H-RetailAudioCountdown: retail writes `0x14998A` and/or `0x14974C` from
  identifiable worker/wait PCs during the gated route; those writers, not a
  decoder change, are the next audio contract boundary.
- H-RetailTaskBoundary: retail executes the known audio-task/AI callsites in
  the same title/hangar phase and carries nonzero task fields; a live gate with
  no task/AI rows selects task admission rather than the RSP image.
- H-Coverage: the whole-RDRAM control, 640/hangar phase, or watched execution
  controls are absent, so the narrow nulls are unevaluable and no audio change
  is authorized.

The discriminator is one phase-keyed table of retail writer/execution PC,
physical target, post-store value or watched GPRs, plus the port's existing
`m5-gate`, audio-task dispatch/return, slot, and PCM rows. H-RetailGateWriters
requires the whole-RDRAM control and named writer/value transitions;
H-RetailAudioCountdown requires a positive countdown/status writer; and
H-RetailTaskBoundary requires both task/AI execution and nonzero task fields.
Any missing positive control selects H-Coverage. A null without the control is
not evidence.

## Exact commands

Retail ground truth, before any port change:

~~~
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --rsp /opt/homebrew/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --input /opt/homebrew/lib/mupen64plus/mupen64plus-input-sdl.dylib \
  --secs 70 --hit-cap 10000 \
  --watch-write 0x0:0x800000 \
  --watch-write 0xA0F50:0xA0F54 \
  --watch-write 0x14998A:0x14998C \
  --watch-write 0x14974C:0x149750 \
  --watch-pc 0x8009173C --watch-pc 0x80091758 --watch-pc 0x80029EF4 \
  --first-watch 0 --detail-watch 1 --pc-hist-watch 1 \
  --pc-phase-log 0x0066A500 --pc-phase-log 0x005D4500 \
  --pc-phase-log 0x0066AA00 --pc-phase-log 0x00696100 \
  --pc-phase-log 0x00696600 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --hold-ms 200 > scratch/agent/s2217_retail_audio_ground_truth.log 2>&1
~~~

Port existing-route control, no build and SIGKILL watchdog:

~~~
cd build
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
  ROGUESQ_LOG_PCM_SANITY=1 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2217_port_audio_ground_truth.log 2>&1 & p=$!
for i in {1..30}; do
  kill -0 "$p" 2>/dev/null || break
  sleep 1
done
kill -9 "$p" 2>/dev/null || true
wait "$p" 2>/dev/null || true
cd ..
~~~

Inspect only whole-RDRAM count, narrow-watch writer PCs/values, watched task/AI
rows, 640 and hangar VI rows, `[m5-gate]`, audio dispatch/return, slot and PCM
controls, and crash/abort markers. Do not add an instrument until the oracle
control and target writer identities are classified.
