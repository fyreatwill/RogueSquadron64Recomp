# Next work unit: discriminate the M5 legacy/real task-scheduler failure

HYPOTHESIS-ID: m5-legacy-real-route

Competing hypotheses:

- H1: declared-size DMEM staging creates a malformed task; the legacy arm's
  task fields remain valid and reaches both target phases.
- H2: scheduler/state corruption is shared or legacy-specific; both arms show
  the same malformed successor/task state or legacy fails while declared does
  not.
- H3: the failure is outside the audio task contract; both arms reach the
  failing scheduler boundary with equivalent fields and fail before phases.

Discriminator: one build and one concurrent capture with declared/real and
legacy/real arms, retaining the retail positive control and both port phase
controls. At the first task-scheduler failure, log task type, ucode/data
addresses and sizes, DMEM staging mode, and scheduler successor state. A
declared-only malformed row selects H1; identical fields with legacy-only
failure selects H2; equivalent rows and pre-target failure in both arms select
H3. Any arm reaching both phases reopens the candidate census.

Before building, inspect the existing task staging and scheduler trace sites:

    rg -n "spTaskSchedulerThread|ucode_data_size|ROGUESQ_AUDIO_LEGACY_UCODE_DMA|m5-rsp-source-hook" src lib tools

Then add one phase-scoped table at those existing sites, build both arms once,
and run the checked-in three-arm recipe with the legacy/real and declared/real
captures concurrently. Do not add candidate PCs or interpret candidate nulls
in this unit.
