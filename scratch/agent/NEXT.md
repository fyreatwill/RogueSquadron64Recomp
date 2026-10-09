# Next work unit (s4409): latch the hangar direct edge across the VI transition

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4408 qualified title and hangar coverage, but the same-run direct-call
join emitted title rows only. Hangar input and AI-boundary/return rows were
live; session 4407 separately saw a hangar `0x80091CB8` row. The likely issue
is that the call executes before the committed VI phase changes.

Competing hypotheses:

- H-pre-phase-call: hangar `0x80091CB8` executes before VI phase 5 is committed;
  a latch joined to the next phase will carry its input/call arguments into the
  hangar return/task row.
- H-no-hangar-call: the s4407 hangar row was a readout interpretation error;
  a pre-phase latch still has no `0x80091CB8` event before hangar input/boundary.
- H-phase-state-mismatch: the call is live but its input/return belongs to the
  preceding phase, so the latch joins to title/640 rather than hangar.

Discriminating measurement: add one bounded latch at the direct callsite that
records the callsite, input, and current VI phase even outside target phases;
consume it on the first hangar VI transition and print one joined row with the
following hangar AI-boundary/return/store/task witness. H-pre-phase-call is
selected by a pre-transition call plus a hangar return/task join; H-no-hangar-
call by no call before the transition with positive controls live;
H-phase-state-mismatch by a call whose phase/origin remains 640/title and has
no hangar join. Build all latch and existing target-phase arms together.

Exact commands:

1. Patch the existing regeneration-safe host probe and build:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
2. Run the qualified route:
   `zsh scratch/agent/run_s4402_m5_title_selector_witness.sh`
3. Inspect only bounded evidence:
   `grep -a -E '\[m5-selector-ai-(call-latch|call-join)|\[m5-selector-(ai-boundary|input|source)|\[audtask-join\]' scratch/agent/s4402_m5_title_selector_witness/port.log | head -200`

Do not repeat caller enumeration. If the route does not reach both title and
hangar buckets, record it as invalid rather than interpreting a null.
