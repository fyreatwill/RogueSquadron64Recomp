# Next work unit

HYPOTHESIS-ID: m5-bus-error-reattribution

s4697: fixed build, 4/4 arms reach hangar with 0 crashes (VOICE_TRIGGER_CHAIN armed).
Open: s4672 overlay-route crash (scratch/agent/s4672_overlay_route/run.log):
fault far=0x38000950e = host base 0x300000000 + zero-extended 0x8000950e; x0=0x80091378
(zero-extended), last-guest-pc 0x80001b08. Same idiom class as s4696 (unsigned literal
instead of S32()), different site.

Unit: find the s4672 overlay-route recipe (grep PORTING-STATE.md "Session 4672"), replay
it 4 concurrent on the fixed build and count crashes. Hypotheses:
- H-fixed-by-s4696: 0 crashes -> s4672 was also the diagnostic; close bus-error family.
- H-other-site: same fault recurs -> locate the zero-extended load (grep generated code /
  diagnostics for unsigned 0x8xxxxxxx literals used as pointers: idiom-class audit, same
  style as the -0x25A4 audit), fix with S32(), name the writer.
Positive control: reaching VI 512 hangar in unaffected arms. Then proceed to M5 plan next step.
