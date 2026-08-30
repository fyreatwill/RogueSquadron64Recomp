# VI-640 request-state input block

Session 3263 (2026-08-29) ran the prescribed local availability audit for the
state edge that should request the post-640 VI mode.

## Result

- `RecompiledFuncs/` is absent from this checkout; the file-count probe found
  zero generated files.
- `applyPendingViChanges` is present only in symbol metadata at
  `0x8001B7F0` with size `0x2AC`, and in the probe template's expected caller
  at `0x80019914`.
- The host VI path forwards/observes `osViSetMode` and consumes committed VI
  registers. It has no state-selection body that can expose the missing
  request branch.
- Existing evidence remains pre-target VI 640 at origin `0x0066A500`; this
  audit added no runtime measurement.

## Discriminator status

The generated body or an independent trace of its state inputs is required.
A live state input with no target request would select `H-RequestState`; a
target request with no commit would select `H-BoundaryConsumer`; an explicit
terminal-route contract would select `H-Phase4SteadyState`. None is
observable from this checkout, so no hypothesis is selected and no VI/audio
behavior change is authorized.

## Next satisfying input

Obtain the generated body/provenance from the configured regeneration host, or
capture the corresponding state inputs in the independent retail oracle. Do
not repeat the scheduler identity capture or add another host-side VI field
until one of those inputs supplies a concrete edge.
