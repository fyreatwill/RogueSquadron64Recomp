# Next work unit: M5 Step 4h predecessor arithmetic/source

HYPOTHESIS-ID: m5-audio-step4f-call-input-producer

Session 4082 qualified predecessor rows at `0x8008D5D0`, `0x8008D5EC`,
`0x8008D614`, and `0x8008D674`: port `$s2` is already zero at the first
stage and the later `$s0` path is zero. A separate retail-oracle run passed
the whole-RDRAM control and recorded 90,484 executions of `0x800923E4`, with
caller `0x8008D710` and nonzero title `$a1` values. The next unit audits the
source arithmetic and its inputs without changing the gate.

Competing hypotheses:

- Hsetup-live: the next earlier setup/source witness matches the retail-shaped
  values, so the producer is earlier than that witness.
- Hsetup-divergent: an earlier source/register is already zero; its first
  mismatch identifies the producer boundary.
- Hsetup-path: the port reaches a different branch/object shape despite both
  phase gates, so same-PC setup rows are not comparable.
- Hcoverage: a required whole-RDRAM, title/hangar, channel-load, or setup
  control is absent.

Discriminating measurement: batch one regeneration-safe witness over the
operands feeding the `0x8008D5D0` multiply and the `0x8008D674` `$s0`
derivation, retain the existing `0x8008D5E4` positive control, and run the
retail oracle with whole-RDRAM plus the `0x800923E4` execution watch and all
observed title/hangar origin variants. Hpre-live selects matching nonzero
predecessor values and moves earlier; Hpre-divergent selects the first
mismatch; Hpre-path selects qualified phases with no comparable rows;
Hcoverage selects any missing control.

Exact preparation/run: use the direct-AUTOPILOT shape in
`scratch/agent/run_s4081_m5_setup_witness.sh`, adding only the new earlier
witness. Run port first, then the oracle; supervise both child PIDs and
SIGKILL them after the required controls. If regeneration is needed, use
`make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake` before running.
Keep the output in a new scratch directory and do not infer a producer from a
port-only zero.
