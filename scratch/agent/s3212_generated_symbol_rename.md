# Session 3212 — generated-symbol rename pivot

The M5 pair remains blocked before title/hangar and the queued M3 audit was
observation-only, so this iteration took the mandated generated-symbol pivot.
The bounded source/map/registration check selected `H-ObjectiveRegistration`:
`0x80106C50` has a callable body, is called by `lvc_initializeObjectTracking`,
and repeatedly invokes `addBooleanCountHandleWrapper` for objective handles.

`tools/rename/generated_symbol_batch.py` renamed `static_4_80106C50` to
`lvc_registerObjectiveBooleanCounts` in the external generated `funcs.h` and
`funcs_49.c` snapshot. The tool changed exactly two files and refuses a silent
no-op. `python3 -m py_compile` passed. The project TOML intentionally keeps
the enclosing `lvc_initializeObjectTracking` range; adding an overlapping
TOML function record would corrupt symbol boundaries. The unresolved
`func_80092F10` live tail and `fake_func_800AE3E4` data fragment were not
renamed.

No runtime build/run was needed for this source-only rename. This is a real
generated-symbol/tool change, not an instrument re-run.
