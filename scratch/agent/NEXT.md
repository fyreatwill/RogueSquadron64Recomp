# Next work unit

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Begin the bounded generated-symbol renaming sweep now that M5 task-family
cadence is closed. First run the existing rename census/tool help and select
one high-confidence companion mapping; do not rename address-encoded or
deliberate `fake_func_*` boundaries. Competing outcomes are: (1) one mapping
has matching companion symbol, generated body, callers, and exact span, so
apply that single mapping; (2) candidates are ambiguous/data-like, so record
the bounded audit and leave them unchanged; (3) the external companion or
generated tree is unavailable, so stop and report the concrete path blocker.

Discriminator: the selected candidate must have independent companion mapping,
live generated body/callers, and exact adjacent/TOML span agreement. A rename
is authorized only when all three agree; otherwise the sweep remains parked.

Exact commands:

    python tools/rename/find_state_machines.py
    python tools/rename/find_callers.py <selected-companion-or-placeholder>
    python tools/rename/rename_generated_symbols.py --help

If a candidate passes the discriminator, make one bounded mapping edit using
the existing rename tooling, verify the diff, and do not regenerate unrelated
functions. If no candidate passes, write the audit result to a new
`scratch/agent/` file and choose the next ranked lead without a build.
