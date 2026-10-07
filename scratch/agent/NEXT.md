# Next work unit: M5 Step 9e — is the rec+0x7C output buffer filled after audio-task completion?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4206: guest side is fully populated in hangar (n=139264): volume rec+0x58 nonzero 100%, source buffers rec+0x2C/+0x40/+0x78 nonzero 100%, rec+0x7C output buffer zero at render return (expected). H-list-zero-volume refuted. Patch the live tree only (tools/apply_s*.py; s4205 and s4206 already applied in N64Recomp/RecompiledFuncs/funcs_24.c); never regen.

Hypotheses:
- H-ucode-drop: the F5 ucode path (HLE/LLE, docs/F5-UCODE-REFERENCE.md) never fills the output buffer.
- H-downstream: output buffer is filled after the task, but the AI DMA / SDL path delivers silence.
- H-wrong-ptr: +0x7C is not the PCM output (could be a state buffer), so zero there means nothing.

Discriminator (one build, one run, s4205_cmdlist.sh recipe): at audio-task completion (find the SP task-done hook for the audio ucode), re-scan the last N records' +0x7C buffers (keep a ring of recent rec pointers) and the AI DMA source buffer at each AI_LEN write; count nonzero bytes. Positive control: the +0x2C source buffers still nonzero in the same row.
Outcomes: +0x7C zero after completion and AI buffer zero => H-ucode-drop; +0x7C nonzero but AI buffer zero => H-downstream; AI buffer nonzero => H-wrong-ptr or silence is not at PCM level.
