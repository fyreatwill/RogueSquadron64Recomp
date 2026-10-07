# Next work unit: M5 Step 4f identify the first zero call input

HYPOTHESIS-ID: m5-audio-step4f-call-input-producer

Session 4079 qualified the `0x8008D710 -> 0x800923E4` call boundary but found
zero port `a1`/`a3`/scaled inputs in hangar where retail's paired oracle calls
have nonzero inputs. The next single experiment is to identify the first
divergent value in `0x8008D6F4..0x8008D70C`.

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
`0x8008D5E4` positive control. Run the direct AUTOPILOT image route port-first,
then the oracle, with phase-gated title/hangar rows. Hsetup-live selects
matching setup values plus an earlier-source pivot; Hsetup-divergent selects
the first mismatching register; Hsetup-path selects a qualified phase run
with no comparable setup rows; Hcoverage selects any missing control.

Exact preparation/run: inspect the retail call with bounded oracle output
before adding a witness; then regenerate with
`python3 /Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py`,
`/Users/williambuckley/Documents/Tools/N64Recomp/build/N64Recomp rogue_squadron.toml`,
`python3 fixup_game_funcs.py`, build with
`cmake --build build --config Debug --target RogueSquadron64Recomp`, and run
the next numbered direct-AUTOPILOT script. Keep all output under a new
scratch directory; launch the port before the oracle and SIGKILL both arms.
Do not change the gate or add a mitigation from a port-only zero.
