# Next work unit: identify the M5 source-construction predecessor

HYPOTHESIS-ID: m5-source-construction-predecessor

Use the qualified s4138 retail writer table and the existing port source/DMA
rows to join the first divergent caller, argument, or source-buffer
construction boundary. Keep image, wait, cap, predicate, slot state, guest
behavior, and host writeback unchanged. Do not repeat the completed watch-index
repair or chase downstream rendering.

Competing hypotheses and discriminator:

- H-retail-port-caller-match: retail and port share the same caller/arguments
  and source buffer, so the split is after the named producer.
- H-retail-port-caller-split: the first divergent caller, source pointer, or
  length appears before the source-span store.
- H-route-invalid: either route loses a target phase or the phase-keyed join
  lacks a positive control.

The s4139 discriminator selected H-retail-port-caller-split: retail title
uses `prev_pc=0x800052C4`, `a0=0x801BB9B0`, `a2=0x88`, while the port uses
`a0=0x80178C80`, `a2=0x298`; retail hangar and port hangar also differ. The
port hook's `ra=0` is an instrument limitation because this generated context
does not preserve a usable return register.

Competing hypotheses and discriminator:

- H-port-entry-setup-split: the port's entry caller or pre-loop argument
  construction differs from retail's `prev_pc=0x800052C4` before the first
  `0x800078EC` store.
- H-port-hook-register-loss: the guest entry matches, but the generated hook
  loses the return register while adapting the MIPS context.
- H-route-invalid: a new paired run lacks the positive control or target gates.

The single measurement is one phase-gated port entry/return trace around the
`rs_memset` loop (entry PC, caller/return-site state, and first argument tuple)
plus the retail `watch-pc-range`/phase-gated previous-PC table already used in
s4139. Matching entry/caller state selects hook-register-loss; a qualified
entry or argument split selects port-entry-setup-split; missing controls or
phases selects route-invalid. Do not change guest behavior or writeback.

Ground-truth preflight completed before instrumentation. The first 45-second
run had a live whole-RDRAM control and 664 source-span stores but no target
phase; the corrected 65-second run with `--hold-ms 150` reached title and
hangar and produced live phase-gated `0x800078EC` rows. The first result is
route-invalid; the second is the accepted control.

Exact commands for this iteration:

```sh
python3 tools/apply_s4140_m5_source_context.py
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 \
  ROGUESQ_LOG_M5_SOURCE_CONTEXT=1 \
  ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' \
  PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 \
  ./build/RogueSquadron64Recomp > scratch/agent/s4140_port.log 2>&1 &
```

The paired retail command is the accepted preflight shape, expanded with the
writer execution table and source-span watch:

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --hit-cap 10000 --watch-write 0x178c80:0x178f18 --watch-pc-range 0x800078d0:0x80007910 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006ab400:512 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006ab400:512 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/s4140_retail.log 2>&1
```

The s4139 run passed the positive control and both target transitions. Before
the next build, use the existing entry/callsite hooks where possible and batch
all entry fields in one Debug build/run.
