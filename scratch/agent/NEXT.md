# NEXT work unit (s873)

HYPOTHESIS-ID: m3-coalescer-state-gate-audit

Perform one source-only, whole-idiom audit of the state gate that should drive
`runVideoFrameTick` past the width-320 boot phase. Do not build or run. Enumerate
every generated-tree read/write and callsite for the frame-tick state at
`0x801163f8`, the phase/VI state used by `runVideoFrameTick`, and the input/audio
gates immediately surrounding its calls to `partitionFramebufferMemory` and
the coalescer. Classify each site as initialization, per-frame update, gate,
or dead/unreachable, and identify the exact value that can keep the gate in
the observed boot state. Do not add a guard or alter behavior.

Competing hypotheses:

- H-port-state-gate: the port has a systematic missing/stale writer or gate
  input that holds the frame-tick state at the boot phase.
- H-retail-driver-only: the generated port gate is complete; the retail oracle
  stall is an emulator/frontend driving issue unrelated to the port state.
- H-audio/input-gate: the gate depends on an audio or input completion path that
  is stubbed or never delivered in the port.

Discriminating measurement: the complete source inventory must identify (or
fail to identify) a writer and gate predicate for every transition-relevant
state value, with independent callsite coverage. A missing/stale port writer
selects H-port-state-gate; complete port coverage with no audio/input dependency
selects H-retail-driver-only; a transition gate whose only producer is an
audio/input completion path selects H-audio/input-gate. An incomplete inventory
is unevaluable and must be fixed before any runtime experiment.

Exact commands from the repo root:

```sh
rg -n "801163f8|runVideoFrameTick|partitionFramebufferMemory|800022F8|waitForAnyAudioSlot|osCont|PAD|audio" RecompiledFuncs src lib/N64ModernRuntime
rg -n "801163f8|runVideoFrameTick|partitionFramebufferMemory|800022F8" docs PORTING-STATE.md | tail -80
```

Read bounded windows around every generated-function hit; do not read the
ledger whole. Record the site inventory and any source-only conclusion in the
session ledger and CURRENT-TRUTH.
