# Next work unit: M5 Step 7 status-03 service-reaping contract audit

HYPOTHESIS-ID: m5-status03-service-reaping-contract

Run one retail-grounded, phase-gated experiment for the status-03 worker
contract described in `docs/M5-AUDIO-PLAN.md` Step 7. Before building, record
these competing hypotheses and use the same build for every arm:

- Hworker-clears: the named `serviceVoicePoolFrame`/retail-equivalent worker
  enters, legitimately writes status zero, and the wait/drain returns cleanly.
- Hworker-missing: the status-03 path reaches the wait/drain but no legitimate
  zeroing writer occurs in the qualified hangar phase.
- Hroute-invalid: the retail whole-RDRAM positive control or either paired port
  arm fails to reach hangar, so worker and writer nulls are unevaluable.

Discriminating measurement: require the oracle whole-RDRAM/title/hangar
controls, paired real-audio image arms at hangar `512 @ 0x006AB400`, worker
entry, the exact status-zero writer, and clean drain/shutdown return. A
worker-entry -> legitimate zero-store -> return chain in both arms selects
Hworker-clears; worker entry with no zero writer selects Hworker-missing; any
missing route/control selects Hroute-invalid. Do not force-clear status 03 or
add a new guard.

Use the existing phase/task/SP/slot/PCM controls and a single batch of
diagnostics. Ground truth must come from the retail oracle before narrowing the
port watch. Build with:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Then run the new phase-gated paired recipe from `scratch/agent/soak_queue/`
or an equivalent self-contained script, with SIGKILL cleanup and all passive
breadcrumbs enabled. Enqueue the soak rather than babysitting it.
