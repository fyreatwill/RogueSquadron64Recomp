# cxd4 mid-task sampler stride

The external cxd4 source tree is not part of this repository. Apply this
iteration's stride change in `mupen64plus-rsp-cxd4` as follows:

- Add `u32 rs64_rsp_mid_stride(void);` to `su.h`.
- In `module.c`, initialize a cached stride from `RS64_RSP_MID_STRIDE`, default
  256, treating zero as 1, and expose it through `rs64_rsp_mid_stride()`.
- In `su.c:run_task`, call `rs64_rsp_mid_sample(PC, rs64_step)` when
  `rs64_step % rs64_rsp_mid_stride() == 0` instead of using the fixed
  `& 0xff` cadence.

The control run with `RS64_RSP_MID_STRIDE=1` produced 136,872 bytes of RSM1
records while the same run's whole-RDRAM watch reached 10,000 callbacks and
479 VI samples.
