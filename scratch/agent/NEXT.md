# NEXT work unit (s2018) — audit missing service dispatch

HYPOTHESIS-ID: m5-service-path-registration-audit

## Work unit

Run one bounded source/binary crosswalk for `serviceVoicePoolFrame`
(`0x8009B5A8`) in the current 45-file generated tree and already-built
binary. Enumerate its overlay registration, generated definition, every
static call/reference, linked symbol, and the existing service/status marker
strings. Do not rebuild, alter status/audio behavior, or run another
phase-gated status join until this dispatch boundary is understood.

## Competing hypotheses and discriminator

- H1: The function is registered and linked, but the current route never
  reaches its caller; the crosswalk has a valid map entry and caller with no
  same-binary dispatch witness.
- H2: Overlay registration or dynamic lookup points elsewhere (or is absent);
  the crosswalk shows a missing/mismatched map entry or symbol address.
- H3: The function is reachable only behind the audio-disabled gate; the
  crosswalk shows a valid caller whose dispatch is conditioned on the stubbed
  audio path.

The discriminator is one table with address, overlay, caller/reference,
linked symbol, and marker evidence. A complete valid map plus caller but no
dispatch selects H1; a missing/mismatched map selects H2; a valid map/caller
with an explicit audio gate selects H3. If the table cannot separate these,
stop and redesign before building or running anything.

## Exact commands

Run from the repository root, keeping each result bounded:

```sh
rg -n -F 'serviceVoicePoolFrame' ../N64Recomp/RecompiledFuncs src lib/N64ModernRuntime
rg -n -F -e '0x8009B5A8' -e '8009B5A8' ../N64Recomp/RecompiledFuncs src lib/N64ModernRuntime
rg -n -F -e 'serviceVoicePoolFrame' -e '0x0009B168' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
nm -an build/RogueSquadron64Recomp | rg -F -e 'serviceVoicePoolFrame' -e '8009B5A8'
rg -n -F -e 'get_function' -e 'func_map' -e 'load_overlays' lib/N64ModernRuntime/librecomp/src | head -160
```

The output must identify whether the same binary contains a registration,
caller, and linked symbol for the guest function. Record the table and the
selected hypothesis in the next ledger entry; do not infer a runtime H1/H2/H3
status result from the s2017 zero worker control.
