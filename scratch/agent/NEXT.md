# NEXT work unit (s2486) — capture the later OSTask descriptor contents

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Build one phase-gated capture that records all sixteen guest words at
`gspTask=0x800377C8` when `spTaskSchedulerThread` calls
`osSpTaskYielded`, and joins that row to the `0x80019D28` event payload plus
the later `osSpTaskLoad`/`osSpTaskStartGo` task pointer. Use the existing
eleven-Start `tools/probe.sh` route only if the capture is needed to reach the
target phase. Do not alter scheduler behavior or remap audio/output.

## Competing hypotheses

- H-DescriptorPopulated: the sixteen words form a populated normal OSTask and
  identify a legitimate later task at the scheduler boundary.
- H-DescriptorStaleOrEmpty: the object has zero/stale fields when yielded, so
  the pointer is only a yield-status descriptor and cannot explain the later
  consumer identity.
- H-DescriptorWriterUnjoined: the fields are populated, but no same-run writer
  or task-start identity join is visible, leaving population provenance open.

## Discriminator

The single run must include a positive control for the existing resolver hook
(`0x8009123C`) and phase-gated rows for: (1) all 16 words at `0x800377C8`,
(2) event payload at `0x80019D28`, and (3) the later task pointer and its
`OSTask.data_ptr` field at each `osSpTaskStartGo`. A populated descriptor whose
identity/fields join to the later task selects H-DescriptorPopulated; a
zero/stale descriptor selects H-DescriptorStaleOrEmpty; populated but
unjoined fields select H-DescriptorWriterUnjoined. A missing resolver control
invalidates the null result.

## Preparation and exact commands

1. Add the complete capture to the durable fixup/instrumentation path, then
   regenerate in the required order:

   `python tools/make_elf.py && build/Debug/N64Recomp.exe rogue_squadron.toml && python tools/fixup_game_funcs.py`

2. Build:

   `cmake --build build --config Debug --target RogueSquadron64Recomp`

3. Run the qualified eleven-Start probe with all passive breadcrumbs and the
   new descriptor capture enabled, phase-gated by VI transitions; capture to a
   non-hidden final path and SIGKILL the process.

4. Report the three joined row classes and resolver-control count in
   `scratch/agent/s2486_m5_descriptor_capture/audit.md`.
