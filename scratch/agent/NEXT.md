# NEXT: qualify the M4 accumulator instrument at hangar origin
HYPOTHESIS-ID: m4-accumulator-boundary

The s4619 corrected route reached hangar on both arms: port and retail both
logged 512-wide origin `0x006AB400`, and retail passed the whole-RDRAM
positive control with 10,000 retained hits. The port M4 logger emitted only
origin-change summaries and zero accumulator rows at hangar. This is an
instrument-boundary null, not a discriminator result.

Competing hypotheses:

- H-arithmetic: the port `ACCH:ACCM:ACCL` tuple disagrees with the local
  VMADH model before VGE, selecting accumulator/product semantics.
- H-vge-store: VMADH matches the model but post-VGE or stored shade bytes do
  not, selecting VGE/store semantics.
- H-source-divergence: the port tuple/store agrees internally while the
  independent retail phase or RDRAM transition differs, selecting source-state
  or execution divergence.

Discriminator: first make the M4 instrument fire a same-run positive control
at `0x006AB400`; a branch-execution summary is not sufficient. Then run one
paired capture where the port row includes `r9`, `v4`, `v0`, all accumulator
halves, post-VMADH `v6`, post-VGE `v6`, and the stored output record, plus the
changing non-M4 accumulator control. Retail must pass its whole-RDRAM watch
and reach the same hangar origin. Arithmetic, VGE/store, or source divergence
is selected only if both controls and the complete row are present.

Run one build, then use the known Start-mash route and keep the phase gate
open across the transient until hangar:

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    env PROBE_BUILD=build PROBE_KEYS='5:start 10:start 15:start 20:start 25:start 30:start 35:start 40:start 45:start 50:start 55:start 60:start 65:start 70:start 75:start 80:start 85:start 90:start 95:start 100:start 105:start 110:start 115:start 120:start 125:start 130:start 135:start 140:start 145:start 150:start 155:start 160:start 165:start 170:start' PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 ROGUESQ_S4563_SKIP= ROGUESQ_NODEFAULT=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_S4457=1 ROGUESQ_LOG_RS_MALLOC=1 ROGUESQ_LOG_RS_FREE=1 ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_FL_ZERO_ADDR=0x1F9CD0 ROGUESQ_FL_ZERO_ALWAYS=1 ROGUESQ_LOG_M4_ACCUM=1 ROGUESQ_M4_PHASE_FROM=1 ROGUESQ_LOG_PHASE=1 zsh tools/probe.sh scratch/agent/s4619_m4_fixed 40 2
    tools/oracle/build.sh && tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace > scratch/agent/s4619_m4_retail_ground_truth.log 2>&1

Before building, inspect the M4 logger and identify the exact positive-control
condition and its expected marker. If no existing control can be made to fire
in the same run, land that bounded instrumentation change first; do not treat
zero M4 rows as evidence. After qualification, matching tuple but differing
store selects H-vge-store; tuple disagreement selects H-arithmetic; matching
port internals with a qualified independent retail phase selects
H-source-divergence. Missing positive control or complete rows is unevaluable.
