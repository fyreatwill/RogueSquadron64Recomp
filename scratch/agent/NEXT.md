# NEXT: paired M4 accumulator boundary capture after the retail name census
HYPOTHESIS-ID: m4-accumulator-boundary

The s4617 capture passed whole-RDRAM, target-span, both PC controls, title VI
1024, and both 512 hangar origins. The five names were present in the target
snapshot, while `0x80007670` had zero target-span writer rows in every 320,
640, 1024, and 512 bucket despite 76 lifetime target-span writes. All 17
pointer-target controls were zero. This is single-source oracle evidence that
the name copy is earlier or on an unarmed path; do not repeat it.

Competing hypotheses:

- H-arithmetic: the captured port `ACCH:ACCM:ACCL` tuple disagrees with the
  local VMADH model before VGE, selecting accumulator/product semantics.
- H-vge-store: VMADH matches the model but post-VGE or stored shade bytes do
  not, selecting VGE/store semantics.
- H-source-divergence: the port tuple/store agrees internally while the
  independent retail phase or RDRAM writer transition differs, selecting
  source-state/execution divergence.

Discriminator: one paired port/retail capture at the first live 512 shaded
phase. The port row must include `r9`, `v4`, `v0`, all accumulator halves,
post-VMADH `v6`, post-VGE `v6`, and the stored output record, plus a changing
non-M4 accumulator control. A retail whole-RDRAM control and VI trace must
prove the corresponding phase. The three outcomes above select exactly one
hypothesis; without both controls the result is unevaluable.

Build/run (port arm, after any required existing-probe rebuild):

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M4_ACCUM=1 ROGUESQ_M4_PHASE_FROM=1 ROGUESQ_LOG_PHASE=1 zsh tools/probe.sh scratch/agent/s4618_m4_paired 20 2
    tools/oracle/build.sh && tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 30 --watch-write 0x0:0x800000 --vi-trace > scratch/agent/s4618_m4_retail_ground_truth.log 2>&1
