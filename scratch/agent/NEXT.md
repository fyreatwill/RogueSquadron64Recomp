# Next work unit: qualify the next M5 retail candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-class

Before building, retain this hypothesis table and discriminator as the
instrument contract. Run the existing phase-gated retail/port candidate-writer harness for
`0x80005018`, `0x8000501C`, and `0x80005020`, with all passive breadcrumb
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
