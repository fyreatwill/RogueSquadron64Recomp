# NEXT: qualify the M4 accumulator capture at hangar origin
HYPOTHESIS-ID: m4-accumulator-boundary

The s4618 M4 attempt was unevaluable. Retail passed the whole-RDRAM positive
control (10,000 hits) but stayed at attract 320/640 for 30 s. The port's
no-input and single-Start arms died before target phase in
`musyxSynthFrame_s4562_impl+5808`; the corrected stale-head recipe reached
only transient 512 origin `0x00690400`, not hangar `0x006AB400`, while
emitting 2,112 M4 rows. Do not interpret those rows as hangar evidence.

Competing hypotheses:

- H-arithmetic: the port `ACCH:ACCM:ACCL` tuple disagrees with the local
  VMADH model before VGE, selecting accumulator/product semantics.
- H-vge-store: VMADH matches the model but post-VGE or stored shade bytes do
  not, selecting VGE/store semantics.
- H-source-divergence: the port tuple/store agrees internally while the
  independent retail phase or RDRAM transition differs, selecting source-state
  or execution divergence.

Discriminator: one paired capture at hangar origin `0x006AB400`, not the
transient `0x00690400`. The port row must include `r9`, `v4`, `v0`, all
accumulator halves, post-VMADH `v6`, post-VGE `v6`, and the stored output
record, plus the changing non-M4 accumulator control. Retail must pass its
whole-RDRAM watch and reach the same hangar origin. Arithmetic, VGE/store, or
source divergence is selected only if both controls are present.

Run one build, then use the known Start-mash route and keep the phase gate
open across the transient until hangar:

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    env PROBE_KEYS='5:start 10:start 15:start 20:start 25:start 30:start 35:start 40:start 45:start 50:start 55:start 60:start 65:start 70:start 75:start 80:start 85:start 90:start 95:start 100:start 105:start 110:start 115:start 120:start 125:start 130:start' PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 ROGUESQ_S4563_SKIP= ROGUESQ_NODEFAULT=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_S4457=1 ROGUESQ_LOG_RS_MALLOC=1 ROGUESQ_LOG_RS_FREE=1 ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_FL_ZERO_ADDR=0x1F9CD0 ROGUESQ_FL_ZERO_ALWAYS=1 ROGUESQ_LOG_M4_ACCUM=1 ROGUESQ_M4_PHASE_FROM=1 ROGUESQ_LOG_PHASE=1 zsh tools/probe.sh scratch/agent/s4619_m4_hangar 40 2
    tools/oracle/build.sh && tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace > scratch/agent/s4619_m4_retail_ground_truth.log 2>&1

Expected outcomes: matching tuple but differing store selects H-vge-store;
tuple disagreement selects H-arithmetic; matching port internals with a
qualified independent retail phase selects H-source-divergence. Missing
hangar or whole-RDRAM controls is unevaluable.
