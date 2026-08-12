# NEXT work unit (after s733 reset-to-reuse correlation)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Build one regeneration-safe, phase-latched source-route trace at `L_1DB0`.
For active depth-0 resets only, retain bounded first/last records of the
return address, resident-overlay id (`DMEM[0x153]`), pre-reset depth, `r17`,
and the pending direct-dispatch opcode/source. Keep the current depth ledger.
Do not add a mitigation.

## Competing hypotheses

- **H-wrong-trigen-route:** every active reset enters `L_1DB0` through the
  `0x05` TriGen overlay relay with the resident/return route that the generated
  overlay splice maps incorrectly; the reset is an accidental execution of a
  bootstrap path in an active `0x06` child.
- **H-intentional-trigen-reset:** active resets use a consistent, valid TriGen
  route and resident id, so the original microcode deliberately clears the
  local frame depth at this mesh boundary; the host's call-depth model is not
  the correct semantic ownership boundary.
- **H-route-mixed:** active resets arrive through multiple source routes, so no
  single overlay-route assumption explains the repeated depth-0 overwrite.

## Discriminating measurement

In one build, call a host probe immediately before the `L_1DB0` reset with
`r31`, `RSP_MEM_BU(0X153, 0)`, old depth byte, and `r17`. Retain records only
when depth 0 is active, together with the pending `L_12A0` direct/overlay tag
and the current inline-probe opcode/route. One uniform active-reset route
matching the `0x05` relay selects H-wrong-trigen-route; a uniform route whose
static semantics show an intentional reset selects H-intentional-trigen-reset;
multiple route tuples select H-route-mixed. Positive controls: the same run
must retain balanced direct-only boot rows and reproduce a section-2 cap row
with reset-active count equal to depth-0 reuse and zero unpaired reuse.

## Commands

    rg -n -C 8 'L_1DB0:|RSP_MEM_B\(0X52, r18\) = 0|rs64_e9prov_l1db0_reset|rs64_inline_probe_dispatch' build/factor5_ucode/factor5_ucode_recompiled.c src/rsp/dpc_bridge.cpp tools/fixup_factor5_ucode.py
    python3 tools/fixup_factor5_ucode.py build/factor5_ucode/factor5_ucode_recompiled.c
    cd build && cmake --build . -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_E9_PROVENANCE=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' zsh ../tools/probe.sh ../scratch/agent/s734_reset_route 300 2
