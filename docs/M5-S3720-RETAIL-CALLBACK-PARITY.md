# M5 s3720 — retail callback-path parity

The independent retail oracle ran with Rice video, the validated Start
schedule, the whole-RDRAM positive control, and a hangar phase gate. The
control reached 10,000 writes, and the run reached 475 VI samples at
`0x006AB400` with width 512. In that target phase, watched guest execution
sites fired independently: `0x80033FCC` 2,449 times, `0x80029E80` 3,639
times, `0x80029F30` 3,639 times, and `0x80094648` 128 times. The two one-shot
setup sites `0x8008EB8C` and `0x8008EBBC` also fired.

This is independent retail evidence that the target route contains multiple
guest-side task/audio paths, consistent with the port's distinct image-stage
and PCM-consumer sources. The oracle cannot expose a host callback thread or
SDL queue ownership, so it does not establish host-thread parity and does not
select between retail shared versus split host callback state. The existing
port-only `H-CallbackOwnershipBoundary` remains valid; retail host ownership
is still open.

ORIGIN: diagnostic-only oracle execution watches and the existing port callback
fields. No guest or host behavior was changed.

Evidence: `scratch/agent/oracle_s3720_callback_parity/oracle.log`.
