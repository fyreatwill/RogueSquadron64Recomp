# Next work unit: M5 Step 4f identify the first zero call input

HYPOTHESIS-ID: m5-audio-step4f-call-input-producer

Session 4079 qualified the `0x8008D710 -> 0x800923E4` call boundary but found
zero port `a1`/`a3`/scaled inputs in hangar where retail's paired oracle calls
have nonzero inputs. Session 4080 installed the setup witness, but its direct
AUTOPILOT route had no hangar setup rows and the probe retry missed its 1024
gate; those nulls are Hcoverage, not a producer result. The next single
experiment is to rerun the witness on the exact qualified s4079 probe route.

The batched witness records source `$s2/$s3/$s0`, prepared `$a1/$a2/$a3`,
and the computed `$v1`/scaled value at `0x8008D70C`, phase-gated to title and
hangar. It is installed in `fixup_game_funcs.py` and survived regeneration.

Competing hypotheses:

- Hsetup-live: the port setup registers match retail at `0x8008D6F4..0x8008D70C`,
  so the zero call inputs originate earlier than this setup sequence.
- Hsetup-divergent: one setup register is already zero on the port; its first
  divergent site identifies the next producer boundary.
- Hsetup-path: the port reaches the call through a different branch or object
  shape, so a same-PC setup witness is not comparable despite target phases.
- Hcoverage: either arm lacks the whole-RDRAM/title/hangar controls or the
  qualified `0x8008D5E4` load control.

Discriminating measurement: use the retail oracle's `0x800923E4` execution
watch with whole-RDRAM and both phase controls. Batch one regeneration-safe
port witness over the setup instructions and retain the existing
`0x8008D5E4` positive control. Run the qualified probe route port-first, then
the oracle, with phase-gated title/hangar rows. Hsetup-live selects
matching setup values plus an earlier-source pivot; Hsetup-divergent selects
the first mismatching register; Hsetup-path selects a qualified phase run
with no comparable setup rows; Hcoverage selects any missing control.

Exact preparation/run: run the retail oracle with `--watch-write 0x0:0x800000`
and `--watch-pc 0x800923E4` plus explicit title/hangar phase buckets, then run
the port with the exact `run_s4079_m5_channel_transform.sh` probe recipe,
adding only `ROGUESQ_LOG_M5_VOICE_MODULATION=1` (the setup witness is already
present). Supervise each child PID directly and SIGKILL the game/oracle after
the required phase controls. Regeneration, if needed, is
then
  `python3 /Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py`,
`/Users/williambuckley/Documents/Tools/N64Recomp/build/N64Recomp /Users/williambuckley/Documents/Tools/N64Recomp/rogue_squadron.toml`,
`python3 fixup_game_funcs.py`, build with
`cmake --build build --config Debug --target RogueSquadron64Recomp`, and run
the next numbered direct-AUTOPILOT script. Keep all output under a new
scratch directory; launch the port before the oracle and SIGKILL both arms.
Do not change the gate or add a mitigation from a port-only zero.
