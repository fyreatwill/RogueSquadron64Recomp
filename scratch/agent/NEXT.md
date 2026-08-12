# NEXT work unit (after s720: host-staged task root is the TriGen refill source)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Measure DMEM 0xFF0 immediately after `factor5_boot` and before the host
runner's `poke_be32(0xFF0, dl_ptr)`. s720 proved the latter is the live
L_1DB0 refill source; this unit determines whether it mirrors the real boot
contract or overwrites it. Retain the existing TriGen route/source row as the
same-run positive control. This is source ownership, not a mitigation.

## Competing hypotheses

- **H-boot-mirrors-host:** boot leaves DMEM 0xFF0 equal to `OSTask.data_ptr`;
  the host stage is redundant and the root seed is part of the real contract.
- **H-host-overwrites-boot:** boot leaves a different nonzero value at 0xFF0;
  host staging replaces the real source and can explain the wrong continuation.
- **H-boot-does-not-initialize:** boot leaves 0/garbage at 0xFF0; task staging
  is necessary, but its correct value must be reconstructed from the boot ABI.

## Discriminating measurement

One phase-scoped task row must report boot-pre-FF0, `OSTask.data_ptr`, and
post-stage-FF0. Equality at boot supports H-boot-mirrors-host; a distinct
nonzero boot value supports H-host-overwrites-boot; zero/garbage supports
H-boot-does-not-initialize. The existing complete 0x05 route and a
`staged_dram==refill_dram` source row are the positive controls.

## Commands

    # Add a phase-scoped pre/post 0xFF0 staging row in factor5_gfx_runner.
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \\
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \\
      PROBE_KEYS="3:start 7:start" PROBE_PHASE_WIDTH=1024 \\
      PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \\
      zsh tools/probe.sh scratch/agent/s721_boot_ff0 60 1
