# M5 session 3548 — real-audio port route requalification

The independent retail oracle could not be rerun because this checkout lacks
its required `libmupen64plus.dylib` core. The retained retail capture remains
phase-valid: its whole-RDRAM control fired and it reached title 1024 and
hangar 512.

One controlled port run used the existing real-audio/LLE/spin-yield/autopilot
settings from `build/`, with SIGKILL cleanup. Startup and 320-VI controls
fired, but the process SIGBUSed before title in `parseHmtMaterials+3588` via
`loadDebugAssets`; `si_addr=0x3800007e0` and the last-guest-PC breadcrumb
remained the stale `0x80001F88`. Audio dispatch, caller, base/index,
destination, and task witnesses were all zero.

This reproduces the route-invalid capture and selects `H-PortAssetInput` at
the current discriminator: the failure occurs before any real-audio task
dispatch, so a scheduler explanation is not supported by this run. It does
not identify the malformed HMT/texture input or its writer. No audio, PCM,
image-task, output, or texture-record state was changed.

ORIGIN: diagnostic-only route and phase observations; no value was suppressed,
rewritten, skipped, or guarded.

Evidence: `scratch/agent/s3548_m5_route_requalification/port.log` and
`result.txt`.
