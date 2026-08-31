# M5 Session 3426 — initN64RspMixer caller arguments

The independent retail oracle ran first with a whole-RDRAM positive control,
execution watches at `0x80091934` and `0x8008F0A0`, and title/hangar phase
logging. The control reached 10,000 callbacks; both phase gates fired. Retail
observed `0x80091934` with `a1=0x561F`, and the callee entry
`0x8008F0A0` retained that value, in both title and hangar rows.

The fresh Debug build added a phase-gated, regeneration-safe witness at
`initN64RspMixer` entry and immediately before its `0x80091934` call to
`allocateSongChannelArray`. Silent and Factor 5 image arms were run together.
Both reached title 1024 and hangar 512; the witness positive control fired in
both arms, audio ABI/DMA controls were live, the image-stage control was live
in the image arm, and neither arm emitted crash or abort markers.

Both port arms had the same tuples:

```text
init entry:   a0=0x80165ED0 a1=0x0000000F a2=0x000000A0 a3=1
pre-allocate: a0=0x0000000F a1=0x00005622 a2=0x000000A0 a3=1
```

Thus the port's `a1=0x5622` is supplied by the caller at the observed
init-to-allocate edge; the callee does not mutate it before entering
`allocateSongChannelArray`. This selects `H-CallerPassesPortCount` and refutes
`H-CalleeMutatesCount` at this boundary. `H-CallerUnevaluable` is also refuted
because the whole-RDRAM, phase, and witness controls all fired. The value's
legitimacy and the earlier producer of the `0x5622` argument remain open.

Evidence: `scratch/agent/s3426_m5_init_mixer_groundtruth/oracle.log` and
`scratch/agent/s3426_m5_init_mixer_pair/{silent,image}.log`.
