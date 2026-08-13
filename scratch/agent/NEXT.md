# NEXT work unit (s859)

HYPOTHESIS-ID: m3-guest-pc-8000834c-audit

Add one behavior-neutral, phase-gated runtime probe at
`getNextSlotNpcTypeId` in the generated-code fixup path. Record, in one
bounded row, the masked selector, slot-table pointer, selected slot address,
`+4` link, linked context pointer, context `+0x16` type, and return value.
Keep the existing dispatcher and E9 provenance controls armed in the same run.
Do not add a guard or alter control flow.

Competing hypotheses:

- H-link-state: the helper reaches a non-sentinel link or context pointer
  outside the KSEG0/RDRAM range or outside the populated slot/context regions;
  a row with that defect before the crash selects this branch.
- H-legitimate-chain: all captured helper chains are valid through the crash
  window; this weakens the helper theory and returns priority to the stale
  breadcrumb/other crash path.
- H-caller-transition: a caller supplies a selector inconsistent with its
  record or consumes a valid helper result in a mismatched state transition;
  caller identity plus the row's selector provenance is required to select it.
- H-stale-breadcrumb: the helper probe remains healthy while the process dies
  with the same host/guest-PC handoff; this keeps attribution unresolved.

Discriminator: the helper row immediately before the death. An invalid link or
context selects H-link-state; valid helper rows plus caller-state mismatch
select H-caller-transition; valid rows and no mismatch select H-legitimate;
zero helper rows despite positive dispatcher/E9 controls keeps H-stale-
breadcrumb open. No outcome authorizes a mitigation without naming the writer
and establishing value legitimacy.

Exact commands:

1. Add the breadcrumb to the regeneration/fixup path, not only to a generated
   output: `rg -n -C 8 "getNextSlotNpcTypeId|80040218" ../N64Recomp/fixup_game_funcs.py`.
2. Regenerate in the required order (`make_elf.py`, N64Recomp, fixup script),
   then build: `cmake --build build --config Debug --target RogueSquadron64Recomp`.
3. Run from `build/` with `PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1`,
   retaining the existing dispatcher/E9 controls and using SIGKILL on timeout.
4. Require positive dispatcher/E9 controls before interpreting helper-row
   absence; compare the final helper row to the crash marker and phase ordinal.
