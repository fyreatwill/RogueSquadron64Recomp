# s2491 M5 descriptor pointer ABI

The Debug build succeeded. Before the port run, the independent retail oracle
whole-RDRAM positive control reached 10,000 callbacks in 8 emulated seconds.

The qualified port run used the eleven boot-relative Start schedule and reached
512 / `0x006AB400` at 25.7 seconds. The descriptor control and descriptor-yield
controls fired 26 times each in the target phase. The scheduler-id control was
not enabled by this recipe, so scheduler rows are not used as evidence here.

In all 26 target comparison rows, every selected field had
`MEM_W == explicit aligned memcpy == TO_PTR`. The raw layout rows independently
retain the aligned OSTask shape. The run later crashed in `submitSceneNodeRender`
with `last-guest-pc=0x80010840`; that is after the discriminator fired and is
not attributed to this ABI change.

This selects `H-pointer-sign-extension-fixed` and refutes
`H-pointer-ABI-not-causal` at the descriptor callback boundary. The callback
still accepts the generated 32-bit identity for joins/logging, but creates a
sign-extended guest address before `MEM_W` and `TO_PTR`. No task dispatch,
audio behavior, or guard changed.
