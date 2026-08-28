# NEXT work unit — map retail 1024-mode writer to the port path

HYPOTHESIS-ID: m5-vi-mode-stall

## Single work unit

Use retail-attributed VI writer PC `0x80035798` and the existing retail
MAP/symbol sources to identify its containing function and mode-descriptor
writer. Audit the matching recompiled function, generated callers, overlay
registration, and current port `osViSetMode` path. Do not modify behavior.

## Competing hypotheses

- H-WriterMissing: the retail writer's containing function or caller is absent
  from the port execution path before the VI-640 stall.
- H-WriterAliased: the port reaches the corresponding code, but overlay or
  symbol dispatch maps the retail writer to a different generated function.
- H-ModeDescriptorCorrupt: the port reaches the writer path, but its legitimate
  mode descriptor is corrupted before the call.

## Discriminating measurement

Build a static identity/call-chain table for `0x80035798` and check the
existing s3056 port log for the mapped function/site. If the containing
function has no port execution/call evidence, H-WriterMissing wins; if it
executes but resolves to a different generated body, H-WriterAliased wins; if
it executes and reaches the mode writer with a non-1024 descriptor,
H-ModeDescriptorCorrupt wins. A function identity alone does not select a
hypothesis; require caller and execution evidence.

## Exact commands

1. `rg -n "80035798|800357" /Users/williambuckley/Documents/Tools/rogue_squadron64 .`
2. Read bounded windows around the matching generated body, header, overlay
   registration, TOML, and callers; record the table in
   `scratch/agent/s3057_m5_vi_writer_mapping/AUDIT.md`.
3. Check `/tmp/port_osvisetmode_s3056_run2.log` for the mapped function/site
   and confirm the four-call table; add no instrument unless static identity
   exposes a specific missing edge.

Expected outcome: one named writer/call-chain classification, or an explicit
unresolved boundary with the next highest-information source named.
