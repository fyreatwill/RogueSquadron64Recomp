# Next work unit: re-qualify the M5 legacy/real route

HYPOTHESIS-ID: m5-candidate-writer-route-qualification

Run one repeat of the same bounded legacy/real paired recipe for
`0x80005270`, `0x80005274`, and `0x80005278`. The s4002 retail arm qualified,
but the port crashed at `0x8000834c` before title/hangar, so the candidate
result cannot be interpreted. Do not add fields or advance the sweep unless
the port reaches both phase controls.

Competing hypotheses:

- H1: the s4002 port crash was transient; a repeat reaches title and hangar,
  making the existing candidate table interpretable.
- H2: the same pre-title `0x8000834c` crash recurs; the route remains
  unevaluable and the candidate sweep must stay parked.
- H3: the port reaches title/hangar and a candidate has a qualified nonzero
  post-target row; the previous null was only an arm failure, not H2.

Discriminator: the port must emit title VI 1024 and hangar VI 512, with no
crash/abort, before candidate rows are considered. A repeat crash selects H2;
full route qualification selects H1, while a qualified candidate nonzero row
selects H3 and identifies a producer edge.

Exact command:

    zsh scratch/agent/run_s4003_m5_candidate_writers.sh

Create the s4003 wrapper by changing the output tag in
`run_s4002_m5_candidate_writers.sh`; it launches the retail oracle and
legacy/real port arm concurrently, captures both logs, and SIGKILLs both after
the bounded window. Do not add another field or run a second soak in that
iteration.
