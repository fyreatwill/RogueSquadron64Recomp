# NEXT: retarget the phase-4 DL pool off the color images
HYPOTHESIS-ID: g1d-widescreen

Session 6201 selected H-base and refuted H-size and H-not-this. Do not
add another write hook. Do not skip, clamp, or restore the color-image
writeback. Do not rerun `scratch/agent/soak_results/s6200/` or
`s6201/` unless this patch changes the logged placement. Do not raise
`osMemSize`. The overlap is top-invariant: carves with `a3!=0` end at
`top-0x100000` because that subtract is hardcoded, and the 448-line
stack hangs off `d8 = top-t0`.

Witness: `scratch/agent/soak_results/s6201/witness.txt`.

Phase-4 `[g1d-task] data_ptr` is the chunk `beginFrameDLChunk` pops at
PC `0x8000A9CC`. Stride `0x108` and pool n=3 bytes `0x4AF58` / arg
`t2=0x4B000` are the same in both 12 MB arms. Carve n=3 (`a3==0`,
store PC `0x80001010`) is the only carve that changes:

- control: `outw=512 t0=0x70000 d8=0x80B90000 e8=0x80B25000`, node `0x80B2D820`
- wide: `outw=796 t0=0xAE200 d8=0x80B51E00 e8=0x80AE6E00`, node `0x80AEF620`

`t0` delta = pool delta = node delta = `(796-512)*448*2` = `0x3E200`.
Pool = `d8 - t1 - t1 - t2` with `t1=0x10000` (`d8-0x6B000`). Chunk
indexes 132 and 190 match. Wide pool `[0xAE6E00,0xB31D58)` intersects
the unchanged image `[0xA95C00,0xB00000)`. f0 `0xB41E00` and f4
`0xB31E00` stay above `0xB00000`. The gap `0xB00000..d8` is `0x51E00`:
the pool alone fits, f0+f4+pool (`0x6B000`) does not. Do not put the
wide pool at the control address `0x80B25000` (that span runs through
wide `d8`). Do not hardcode `0x3E200`.

One opt-in patch, regeneration-safe in `tools/apply_s6031_far.py`.
On the `0x80001010` store only, and only when this carve's outgoing
width was rewritten (`outw != 512`, the existing `wv>0` path), overwrite
the `0x801163E8` global with a span of length `t2`. Do not change `t0`,
`d8`, `dc`, f0, f4, f8, or ec, and do not touch the `0x80000FFC` store.
Read `0x80001010..0x80001084` before clobbering `r3`; patch the global
if the register is reused. Retail `outw==512` must keep e8 `0x80B25000`.

Candidate to test, recomputed from the logged registers, not from the
constants above: `ec - t2` (the `0x801163EC` value minus `t2`, aligned
the same way the guest aligns). On the s6201 wide numbers that is
`[0x96D800, 0x9B8600)`, which misses d8, f0, f4, f8, ec, and the
writebacks that end at `0xB00000`. Reject it if the main-heap end
(the s6127 heap high-water, not the DL freelist at `0x801163B0`) is
above that base. If the hole is occupied, log the two bounds and stop.
That is a result. Do not guess a second address in the same run.

Also extend the existing phase-4 `[g1d-task]` line in
`src/main/main.cpp` (`rs64_run_lle_gfx`) to print the big-endian words
at `data_ptr+0x28` and `data_ptr+0x78`, still gated on
`ROGUESQ_LOG_G1D_TASK`, first rows only. The fill is what the RSP sees
at task time. An alloc-time read is not a pass: the image pixels are
already there before the chunk is popped.

Build once:
`env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp`

Then the s6201 recipe, sequential, from `build/`, SIGKILL, screen
unlocked, one game at a time:
`ROGUESQ_OSMEM_MB=12 ROGUESQ_LOG_G1D_TASK=1 ROGUESQ_LOG_PHASE=1`
`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1`
`ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1`
with `ROGUESQ_ASPECT=4:3` then `16:9`. Do not pass `ROGUESQ_FB_WIDTH`.

Pass: control e8 stays `0x80B25000`, data_ptr stays `0x80B2D820`, and
the task-time word at +0x78 is `05200002`. Wide data_ptr lies inside
the new span, outside every `[g1d-carve]` image (`d8`/`dc` of n=0..3
and the spans that end at `top-0x100000`), +0x28 is not `00010001`,
and +0x78 is `05200002`. A null `[g1d-carve]` / `[g1d-alloc]` /
`[g1d-task]` line is a blind hook: fix it and rerun.

If the wide address misses the images but +0x78 is not `05200002`,
stop. That selects the phase-3 `swl` at `0x8000D5A8` (it still writes
`0xB2D898` and does not retarget a moved node). Do not add a writeback
hook for that outcome.
