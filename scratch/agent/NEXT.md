# Next work unit: qualify the next M5 retail candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-class

Before building, retain this hypothesis table and discriminator as the
instrument contract. First make an address-only copy of
`scratch/agent/run_s3933_m5_candidate_writers.sh` as
`run_s3934_m5_candidate_writers.sh`, changing every candidate reference to
`0x8000503C`, `0x80005040`, and `0x80005044`. Then run
`cmake --build build --config Debug --target RogueSquadron64Recomp` once and
`zsh scratch/agent/run_s3934_m5_candidate_writers.sh`; the script launches
the phase-gated retail/port candidate-writer harness for
`0x8000503C`, `0x80005040`, and `0x80005044`, with all passive breadcrumb
instruments enabled. Build once, then run the retail oracle and paired port
arm concurrently from `build/`; use SIGKILL for watchdog cleanup. The wrapper
must record whole-RDRAM, title-1024, hangar-512, and oracle-completion
positive controls before interpreting candidate rows.

Competing hypotheses:

- H1/H2: a candidate writes a legitimate nonzero target payload; it executes
  in the qualified target phase and produces a post-target scalar/value row.
- H3: these candidates are disconnected from the target writer; controls pass
  but candidate execution or post-target rows remain absent.
- H4: the retail arm is unevaluable; a control or target phase fails, so no
  writer conclusion is allowed.

Discriminator: candidate execution plus a post-target scalar/value row during
the qualified target phase, with all four positive controls passing. The paired
port arm must reach hangar and report its image-DMA payload separately; it is
not a substitute for retail attribution.
