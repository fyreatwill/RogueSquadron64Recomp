# NEXT work unit (s1038)

HYPOTHESIS-ID: m4-accumulator-origin

Perform one new, phase-gated M4 numeric-origin capture. Extend the existing
regeneration-owned M4 probe to record every lane of the pre-VGE `vmadh
v6,v4,v0` result, its `acch/accm/accl` tuple, the selected `v29` lane, and the
final shade lane, with separate phase-scoped caps for stage-1 controls and
target rows. Build once and run one corrected LLE arm at VI-1024. Do not
change RT64 shade decoding or add a mitigation.

## Competing hypotheses and discriminator

* `H-saturated-high-half`: the sentinel is VMADH saturation; pre-VGE
  accumulator high halves hit `0x8000` with overflow evidence.
* `H-in-range-sign-extension`: the sentinel is an ordinary in-range VMADH
  result whose sign-extended middle word is `0x8000`; high halves show no
  saturation evidence.
* `H-vge-selection`: the sentinel is already present in selectable `v29` or
  pre-VGE `v6`, so one of those lanes equals the final `0x8000` pattern.

Discriminating measurement: classify the first complete pre-VGE/final tuple
that follows a passing stage-1 control. A saturated high-half selects the first
hypothesis; a non-saturated middle-word path selects the second; an already-
sentinel selectable lane selects the third. If no endpoint is captured, the
run is a controlled null and classifies none of them.

## Exact commands

```sh
python3 tools/make_elf.py
python3 tools/fixup_factor5_ucode.py
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_M4_ACCUM=1 ROGUESQ_LOG_M4_ACCUM_MAX=2048 ROGUESQ_LOG_M4_STAGE1_MAX=64 ROGUESQ_LLE_FORCE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 tools/probe.sh > scratch/agent/m4_s1038_capture.log 2>&1
```

Positive controls required in the same run: VI-1024, all 64 stage-1 controls,
and the existing VMADH control. Analyze only phase-scoped rows and record
whether each endpoint test fired.
