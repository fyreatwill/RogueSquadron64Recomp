# Session 3192 — M5 Step 1 contract pair

Command: `zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh
s3192_m5_step1_contract_pair`

The target rebuilt successfully with the existing checked-in instrumentation.
The retail oracle gate passed before the port arms launched: whole-RDRAM
control reached 10,000 callbacks, title `1024 @ 0x00790400`, and hangar
`512 @ 0x006AB400`. The harness then launched silent (`ROGUESQ_AUDIO_UCODE=0`)
and image (`ROGUESQ_AUDIO_UCODE=1`) arms concurrently and killed all three
processes with SIGKILL at the pair deadline.

Both port arms visibly passed the dispatch control: 80 sampled
`[audtask-dispatch]` rows each, with the expected `real_ucode=0` and `1`
labels. Both issued one pre-title `vi_width=640 origin=0x0066A500` phase and
zero title `1024` or hangar `512` phases. The silent arm had one host
`[filter-voice-audit-control]` positive-control row; neither arm had
target-phase task ABI/DMA/image-stage, audio-return, PCM source/consumer, or
gate rows. The harness summary was `pair_gate=failed silent_hangar=0
image_hangar=0`.

Selection: `H-BothPreTarget`. The arm selector and dispatch controls are
qualified, but the Step 1 target-phase contract row is invalid because both
port arms stop at VI 640 before the required title/hangar phases. This does
not distinguish audio degeneracy from an upstream route stop and does not
authorize a gate, wait, voice, PCM, or task-output change. The next valid M5
qualification requires a route change or equivalent new retail-grounded
boundary.
