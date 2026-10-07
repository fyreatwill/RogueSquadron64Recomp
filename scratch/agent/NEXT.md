# Next work unit: M5 Step 4e scaled channel result into voice modulation

HYPOTHESIS-ID: m5-audio-step4e-channel-transform

Session 4078 qualified the port `0x8008D5E4` reader of the
`0x80141AD8..0x80141AEC` span. The next single experiment is to identify
whether its scaled result reaches `setVoiceModulationParams` at the callsite
`0x8008D710` and changes downstream voice state.

Competing hypotheses:

- Htransform-live: retail executes `0x800923E4` after the channel calculation,
  and the port reaches the matching `0x8008D710` call with retail-shaped
  scaled arguments and downstream voice-state activity.
- Htransform-absent: retail has the target call in title/hangar but the port
  has no matching phase-scoped call witness after `0x8008D5E4`.
- Htransform-value: both arms reach the transform, but the port's scaled
  result or destination voice-state write differs from retail.
- Hcoverage: either arm lacks the whole-RDRAM/title/hangar controls or the
  qualified `0x8008D5E4` load control, making a null unevaluable.

Discriminating measurement: first use the retail oracle to watch PC
`0x800923E4` in the title/hangar phase while retaining the whole-RDRAM control.
Then batch one regeneration-safe port witness at `0x8008D710` and one bounded
downstream voice-state witness, and run one same-build port-first/oracle-second
capture with `PROBE_PHASE_WIDTH=1024` and `PROBE_KEYS_FROM_PHASE=1`.
Htransform-live selects paired call rows and matching downstream state;
Htransform-absent selects valid controls plus retail target calls but zero port
call rows; Htransform-value selects paired rows with a scaled-argument or
state-write mismatch; Hcoverage selects any missing control.

Exact preparation/run: inspect the retail transform with bounded `rg`/oracle
watch output before adding a witness; then regenerate with
`python3 /Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py`,
`/Users/williambuckley/Documents/Tools/N64Recomp/build/N64Recomp rogue_squadron.toml`,
`python3 fixup_game_funcs.py`, build with
`cmake --build build --config Debug --target RogueSquadron64Recomp`, and run
`zsh scratch/agent/run_s4079_m5_channel_transform.sh`. Keep all output under a
new `scratch/agent/s4079_m5_channel_transform` directory; launch the port
before the oracle to avoid the invalid oracle-first scheduler topology, and
SIGKILL both arms. Do not change the gate or add a mitigation from a port-only
zero.
