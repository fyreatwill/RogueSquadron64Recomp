# NEXT work unit (s2136) — retail task-buffer contract

HYPOTHESIS-ID: m5-task-buffer-contract

## Work unit

Run one independent retail-oracle census of the fixed `aspTask` at physical
`0x149470` before adding or changing any port instrumentation. Capture the
qualified `M_AUDTASK` writes and the four task-field pairs that can split the
existing `factor5b_rsp.toml` contract: `ucode`/`ucode_data`, `data_ptr`/
`data_size`, and `output_buff`/`output_buff_size`. Use the same run's
whole-RDRAM watch as the positive control, and phase-gate the target samples
through title and hangar. No build, runtime change, task-field rewrite, new
RSP config, or default-arm change is in scope.

## Competing hypotheses and discriminator

- `H-RetailTaskMatchesFactor5b`: after a qualified `runMusyXTaskLocked` call,
  retail writes `aspTask.ucode=0x80099FE0` and `ucode_data=0x800A4E00`; the
  meaningful buffer is `data_ptr`/`data_size`, with the generated image's
  `data_ptr+0x100` output convention and `output_buff` unused or zero.
- `H-RetailOutputBuffContract`: the retail task uses nonzero
  `output_buff`/`output_buff_size` as the output consumed by AI/voice code;
  the generated `data_ptr+0x100` write is not the final output contract.
- `H-RetailCpuMORTBoundary`: the retail MORT descriptor/CPU voice path is
  live, but no qualified `M_AUDTASK` field transition links it to the
  factor5b data/output convention; the RSP image is not the MORT boundary to
  validate next.
- `H-RetailTaskBoundaryUnresolved`: the oracle run reaches the positive
  control and task PCs but the fixed task rows are absent, conflicting, or
  phase-unqualified, so no ABI conclusion is valid.

The one discriminating table is keyed by `aspTask` field and phase: writer
PC, post-store value, task ordinal, and whether the value equals the
factor5b prediction. Select `H-RetailTaskMatchesFactor5b` only when the
ucode/data image pair and `data_ptr+0x100` convention co-occur with a zero or
unused output buffer. Select `H-RetailOutputBuffContract` only when the
nonzero output buffer is the downstream audio buffer. Select
`H-RetailCpuMORTBoundary` only when the MORT/CPU execution controls pass but
the task rows show no factor5b output relationship. Otherwise select
`H-RetailTaskBoundaryUnresolved` and do not change the port.

## Exact command

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 60 --hit-cap 10000 --vi-trace \
      --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
      --watch-write 0x0:0x800000 \
      --watch-rw 0x149470:0x1494B0 \
      --watch-write 0x149480:0x149484 \
      --watch-write 0x149488:0x14948C \
      --watch-write 0x1494A0:0x1494A4 \
      --watch-write 0x1494A4:0x1494A8 \
      --watch-write 0x149498:0x14949C \
      --watch-write 0x14949C:0x1494A0 \
      --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 \
      --post-value-watch 4 --post-value-watch 5 --post-value-watch 6 \
      --post-value-watch 7 --pc-hist-watch 1 \
      --watch-pc 0x8008E904,0x80091EB0 \
      --detail-watch 8 --detail-watch 9

Watch indexes are intentional: 0 is whole-RDRAM; 1 is the full `aspTask`
range; 2/3 are `ucode` and `ucode_data`; 4/5 are `data_ptr` and
`data_size`; 6/7 are `output_buff` and `output_buff_size`; 8/9 are the two
execution watches. Inspect the bounded post-value and PC-histogram rows plus
the VI 1024/title and VI 512/hangar controls. Do not interpret a null from a
phase the run did not reach.
