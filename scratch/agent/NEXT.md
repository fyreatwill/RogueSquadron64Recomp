# NEXT work unit (s861)

HYPOTHESIS-ID: m3-host-crash-idiom-audit

Perform one bounded, source-only audit of the next recurring host crash idiom
independently of the now-disqualified `0x8000834c` breadcrumb. Start from the
latest repeated local-symbol crash family in the ledger, enumerate every
source callsite and state transition in that idiom, and classify every site as
valid, proven dead, or requiring a writer/legitimacy probe. Do not build or
run until the inventory names a single discriminating runtime boundary.

Competing hypotheses:

- H-idiom-valid: all sites in the selected host crash idiom have valid source
  preconditions and the crash is outside the idiom.
- H-idiom-state: one complete site class has an unproven state transition that
  can be measured at a phase-gated boundary.
- H-idiom-dead: the selected path is unreachable in the relevant phase and
  should be closed without a runtime change.
- H-unresolved: source ownership is complete but no single measurement splits
  the branches; leave the family open.

Discriminator: every possible source classification must map to one outcome:
the selected idiom has no invalid precondition (H-idiom-valid), one complete
site class has a measurable bad-state writer (H-idiom-state), the path is
unreachable (H-idiom-dead), or no single probe separates the hypotheses
(H-unresolved). No outcome authorizes a mitigation without naming the writer
and establishing value legitimacy.

Exact commands:

1. Use `grep -n "local-symbol artifact\\|host-symbol" PORTING-STATE.md | tail -20`
   to select the latest repeated host family, then `rg -n` its symbol and all
   callers in `src`, `lib`, and `../N64Recomp/fixup_game_funcs.py`.
2. Read bounded windows and enumerate every site before changing files. If the
   inventory produces a single discriminating boundary, batch all needed
   instrumentation in the fixup path, regenerate, and build once; otherwise
   remain source-only.
3. If a run is justified, use the existing phase-gated recipe with positive
   controls and queue any repeat soak under `scratch/agent/soak_queue/`.
