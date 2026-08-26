# NEXT work unit (s2489) — separate gspTask byte layout from pointer-base hypotheses

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Add one phase-gated diagnostic to `rs64_m5_descriptor_yield` that captures the
64 raw bytes at `gspTask=0x800377C8` and, for every 32-bit field, prints all
three explicit interpretations in the same row: aligned host word, host word
from byte offset `^ 3`, and byte-swapped aligned word. Also print the guest
address used for each interpretation. Retain the scheduler-id control. Do not
change task dispatch, audio behavior, or any guard.

Before building, verify the byte-address formulas against `MEM_W` and the
RDRAM-copy convention in `librecomp/src/sp.cpp`. Build one Debug binary and
run one qualified hangar capture with the same recipe as s2488.

## Competing hypotheses and discriminator

- H-MEMW-is-logical: aligned `MEM_W` is the logical guest word and the
  implausible values are genuinely stored at this pointer. This predicts the
  aligned interpretation is stable while neither alternate is a valid OSTask.
- H-byte-lane-transform: the callback RDRAM byte layout requires `^3` or byte
  swapping. This predicts one alternate yields type 1/2 and RDRAM-range
  pointer fields consistently across rows.
- H-pointer-base-wrong: `0x800377C8` is not the descriptor base used by the
  proposed field decoder. This predicts none of the three transforms yields a
  coherent OSTask; a neighboring documented base would be needed, but must
  not be searched until the three-way table is recorded.

The discriminator is one same-run transform table with the scheduler-id control
firing in the 512 / `0x6AB400` phase. A coherent type/pointer tuple in exactly
one transform selects the representation hypothesis; three incoherent tuples
leave the pointer-base hypothesis open. The retail oracle remains unavailable
until its debugger-enabled core dylib is installed, so do not interpret a
port-only null as retail evidence.

Exact run command:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_DESCRIPTOR=1 ROGUESQ_LOG_M5_SCHEDULER_ID=1 ROGUESQ_LOG_M5_SECOND_EXEC=1 ROGUESQ_LOG_AUDIO_RETURN=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=300 PROBE_KEYS='15:start 30:start 45:start 60:start 75:start 90:start 100:start 110:start 120:start 130:start 140:start 150:start 165:start 180:start' PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s2489_m5_descriptor_layout 120 1`
