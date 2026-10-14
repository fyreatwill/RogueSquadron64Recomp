# Next work unit (M5 A16 AI-shim caller qualification)

HYPOTHESIS-ID: m5-a16-ai-shim-caller

WORK UNIT: qualify whether the live image-route port calls
`osAiGetStatus_recomp` or `osAiGetLength_recomp`, with independent retail
AI/VI controls in the same invocation. This is observational; do not change
the shims.

Competing hypotheses:

* H-A16-live-caller: a phase-gated port AI status/length caller fires, and its
  result joins nonzero PCM plus a retail AI busy/length transition.
* H-A16-unreached: title/hangar and PCM are positive but no AI shim caller is
  reached; the shims are not a covered-route explanation.
* H-A16-route-invalid: the port route or independent retail controls fail, so
  caller absence is unevaluable.

DISCRIMINATING MEASUREMENT: require title/hangar, task/SP completion, nonzero
PCM, phase-gated `[ai-status]`/`[ai-length]` caller rows, and retail
whole-RDRAM, title/hangar VI, and AI busy/length controls. Caller plus matching
port/retail transitions selects H-A16-live-caller; a positive route with zero
caller rows selects H-A16-unreached; missing controls selects
H-A16-route-invalid.

Exact commands:

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    rg -n "osAiGet(Status|Length)|ai-status|ai-length|AI_STATUS" src lib RecompiledFuncs tools/oracle
    zsh scratch/agent/run_sXXXX_m5_a16_ai_caller.sh

Before building any new probe, run the existing oracle with its whole-RDRAM
positive control and inspect the current port AI-call sites; batch all caller,
busy, length, PCM, and phase fields in one build/run.
