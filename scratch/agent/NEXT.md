# NEXT: G1d game-over sliver — name the writer of the undrawn 21:9 block (H-overlap)
HYPOTHESIS-ID: g1d-menu-sweep

s6728: the game side is clean (identical texrects, complete texture, no overdraw; RT64 texture cache 0 misses). The block
x 640..768 rows 0..N (N 13..128) of cimg A40000/B20000 stays undrawn for ~7 swaps at 21:9. Lead H-overlap: guest writes
land inside the widened colour images (w219: B21578 written ~2250x by rsp_dmem_to_rdram; bzero PC 0x800078EC dst
0x80A0B000 len 0x55000 covers A40000 rows 0..63). Records carry no swap stamp, so their timing vs epoch 27 is unknown.
Hypotheses:
- H-overlap-rsp: RSP DMA (gfx output/yield buffer) writes the corner pixels after RT64's writeback; RT64 then re-reads them.
- H-overlap-heap: a guest heap object (bzero / decompress) lives there on the epoch's first swaps.
- H-rt64: no guest write lands there on swaps 0-6, so RT64 itself drops the pixels (then test FBOVL_SKIP on a bright photo,
  and RT64 fb discard/upload regions).
Instrument (one build): add swap number + rs64_g1d_vi_epoch to rs64FloorWriterRecord (lib/rt64 framebuffer_renderer.cpp;
pass via an extern "C" int counter bumped in upstream_compat swap), and log the guest PC/ra/len for rsp_dmem_to_rdram
records. Run scratch/s6728/gameover.sh w2 21:9 "ROGUESQ_FB_DUMP_EPOCH=27 ROGUESQ_FB_DUMP_VI=1 ROGUESQ_FLOOR_DEPTH_DIR=<dir>
ROGUESQ_FLOOR_WATCH=A41578,A4F578,A5D578,B21578,B2F578,B3D578,A41258,B21258"
(rows 2, 30, 58 at x 700; controls x 300). Discriminator: the epoch-27 swap 0-6 writers of the block words that the
controls lack. Fix must be the root (move the colour images / RSP buffer apart), with a 4:3 + flight regression check.
Then: owner contact sheet per aspect, then G3 render fidelity.
