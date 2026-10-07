# Next work unit: M5 Step 4g earlier setup producer

HYPOTHESIS-ID: m5-audio-step4f-call-input-producer

Session 4081 qualified `0x8008D70C`: the port's hangar setup rows have zero
`s2`/`s0`/`a1`/`a3`/scaled while `s3` matches nonzero `a2`; s4079's paired
retail calls had nonzero inputs. The next unit audits the earlier writer/input
boundary without changing the gate.

Competing hypotheses:

- Hsetup-live: the next earlier setup/source witness matches the retail-shaped
  values, so the producer is earlier than that witness.
- Hsetup-divergent: an earlier source/register is already zero; its first
  mismatch identifies the producer boundary.
- Hsetup-path: the port reaches a different branch/object shape despite both
  phase gates, so same-PC setup rows are not comparable.
- Hcoverage: a required whole-RDRAM, title/hangar, channel-load, or setup
  control is absent.

Discriminating measurement: batch one regeneration-safe witness over the next
earlier setup/source instructions feeding `$s2` and `$s0`, retain the existing
`0x8008D5E4` positive control, and run the retail oracle with whole-RDRAM plus
the `0x800923E4` execution watch and both phase buckets. Hsetup-live selects
matching values and moves earlier; Hsetup-divergent selects the first mismatch;
Hsetup-path selects qualified phases with no comparable rows; Hcoverage selects
any missing control.

Exact preparation/run: use the direct-AUTOPILOT shape in
`scratch/agent/run_s4081_m5_setup_witness.sh`, adding only the new earlier
witness. Run port first, then the oracle; supervise both child PIDs and
SIGKILL them after the required controls. If regeneration is needed, use
`make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake` before running.
Keep the output in a new scratch directory and do not infer a producer from a
port-only zero.
