# NEXT: identify which render call site supplies the ASCII-shaped stream input
HYPOTHESIS-ID: m5-audio-destub

Completed s4594: retail again qualified the B0-pointer role. The first port
probe was gated on VI-512 and passed four controls but was a phase mismatch;
the bad FE98 row appeared after VI-640/origin `0x006A2900`. The corrected
same-run census passed four VI-640 controls and captured
`node=0x8017DE30`, `node+4=0x8017DD58`, `a1=0x6C63745D`,
`a3=0x6C617465`, `computed=0x6C637265`. H-caller-input is selected over
H-cache-node. The run ended at the known odd-PI alignment abort.

Next work unit, in order:

1. Run `zsh scratch/agent/s4591_oracle_tag.sh` and require its whole-RDRAM
   control plus VI origin `0x006AB400`/width 512. Treat the existing retail
   writer rows as the independent role control; do not infer a caller defect
   from a port-only null.
2. Add one regeneration-preserved diagnostic script
   `tools/apply_s4595_caller_input_probe.py`, then build once with:
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   build --config Debug --target RogueSquadron64Recomp -j4`.
   Instrument all four `musyxRenderVoiceSamples` call sites
   (`0x8009024C`, `0x800902CC`, `0x8009039C`, `0x800903F0`) and the
   `fillSampleStreamRange` entry/subtraction. Log voice `+0x34`, constructed
   `a1/a2/a3`, source PC, and the first ASCII-shaped value, phase-gated on
   VI-640/origin `0x006A2900`; retain an adjacent-range positive-control row.
3. Run from `build/` with `ROGUESQ_LOG_S4595=1`, the qualified LLE/solo
   environment, `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, and the
   existing Start schedule in the s4594 recipe. Interpret outcomes:
   - one named call site first emits ASCII-shaped `voice+0x34/a1/a3` while
     the control fires: H-caller-input-source selected;
   - all four inputs remain valid but the subtraction becomes ASCII: reopen
     H-cache-node/translation with a new writer measurement;
   - no target rows without the control: route/phase invalid, no conclusion.

Discriminator: the earliest of the four named call-site rows whose source
operand is ASCII-shaped, with a same-run control and VI-640 gate. Do not add
a mitigation.
