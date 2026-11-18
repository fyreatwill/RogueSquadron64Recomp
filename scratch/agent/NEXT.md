# NEXT (s7563)
HYPOTHESIS-ID: regen-fidelity-drift

19b(e) CLOSED s7562 (s7375 OPEN 0, now a regen_replay gate). Unit: 19b s7420_parser_census OPEN 1 —
tools/fixup_patches_host.py STANDALONE weak-blind since s7490. Run `python3 tools/s7420_parser_census.py --check -v` (see its
--help) and read the open row.
Hypotheses: H-blind (the census parser cannot see the weak decl/STANDALONE block form fixup_patches_host.py emits since s7490 ->
teach the parser, positive control = a planted weak-blind row must still open) vs H-real (a real STANDALONE patch whose weak
symbol is never resolved -> fix the fixup, rerun regen_replay) vs H-stale (the row names text that no longer exists -> drop
the row with a verdict). Discriminator: does the named site exist in the current fixup_patches_host.py output, and does nm on
the built binary show the weak symbol resolved?
Then add s7420 --check to regen_replay.sh if it is not already a gate; fresh regen_replay ok (cp -R scratch/s7558/pristine D/replay).
Then 19b(c): fold s7558_b40_ab when SOAK-RESULTS has it (voided 4/5 so far), then ask the owner about the B40 default.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
