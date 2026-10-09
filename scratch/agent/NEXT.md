# Next work unit (s4461): identify 0x800853A8 and its consumers (lead D)

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4460): the only 'W' store with value 0x80193C18 is pc 0x800853A8 (first 0x80085424) filling a 0xC-stride table at 0x8013B060.. at VI 1024; no C18 store into pool nodes/head (0/6 arms; no +5436 crash occurred). A refuted.
Hypotheses: (D) the 0x8013B0xx table entries are read as pool/list nodes by some consumer (dangling ptr); (C) pool node reused/unlinked; (E) C18 table entries are legit (e.g. sentinel) and unrelated to +5436.
Discriminator: grep the recompiled func containing 0x800853A8 (RecompiledFuncs), read it; then add a load-watch (rs64 load hook or s4457 style) on addresses 0x8013B060..0x8013B140 logging reader pcs; positive control = the 0x800853A8 stores themselves. D: a reader pc inside musyxSynthFrame/list walk or follows the C18 ptr; E: readers are unrelated gameplay code.
Run: build, zsh scratch/agent/s4459_run.sh.
