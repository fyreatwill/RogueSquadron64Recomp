# M5 session 3547 — caller/input producer capture

The regeneration-safe caller witness was added immediately before and after
the direct `loadTextureToMemory` call at `0x80022ACC`/`0x80022AD4`. It records
the caller registers, the `0x20`/`0x24` input fields, and the post-call return;
the existing base/index witness remains enabled for the same target phases.
The build completed successfully and no game state or record write was
changed.

The independent Rice oracle passed the whole-RDRAM positive control, reached
title VI 1024 and hangar VI 512, and observed the caller and callee execution
PCs. Its execution histogram identifies `0x80022ACC` as the predecessor of
`0x8001F954`, with 910 paired executions in the run; the index and table-base
PCs also executed 907 times. The phase-gated field rows were live in both
target phases.

The same-build real-audio port arm was not phase-valid: it crashed before the
first target VI in the existing `parseHmtMaterials+3588`/`loadDebugAssets`
path with `last-guest-pc=0x80001F88` and SIGBUS. The new caller, base/index,
and destination witnesses therefore emitted zero rows. This selects
`H-CaptureInvalid` for the port comparison, not caller parity or divergence;
the caller/input boundary remains open. The oracle is an independent positive
line, while the port crash is the second line establishing why the join cannot
be interpreted.

ORIGIN: diagnostic-only caller and execution witnesses; the legitimate
texture-record operations and all audio/PCM/output state remain unchanged.

Evidence: `scratch/agent/s3547_m5_caller_input_producer/oracle_gpr.log`,
`scratch/agent/s3547_m5_caller_input_producer/port_target.log`, and the
earlier invalid-launch logs in the same directory.
