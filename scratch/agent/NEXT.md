# NEXT: name the writer of the 0x0000 words at guest depth 0x00B56000
HYPOTHESIS-ID: g1d-levelselect-ram

s6626 selects H-guest and refutes H-upload. One Debug binary, both widths.
16:9 35.5 s / 21:9 33.5 s, 52 good frames, alive, 0 crash markers. The only
depth copyFromChanges is state.cpp:2604 on the 21:9 floor depth texture
1024x339. Guest address 0x00B56000, stride 2048, rowStart 0, lookup address
equals store address. ColorConverter::D16::toF of the shader-endian guest
words (rawBe) matches the GPU columns on all 142 samples, max abs 0.
clearDepthTarget read back 1.0 (142/142) on that texture before the upload.
floor-enter matches the upload with max abs 0. The head words are literal
0x0000: x=16 for y=180..192 (13 words) and x=1007 for y=180..191 (12 words).
0x0000 is not the RDP depth-clear word. Later rows of the same columns
include 0xFFFC, which decodes to 1.0, and words such as 0x9E40 (~0.967).
16:9 has no copyFromChanges. Its one depth copy is copyFromTarget at
state.cpp:2570, floor-enter is all 1.0, and shader_11 stores z
0.99416..0.99574. Magenta and pix-match pass. workload_queue.cpp:966 and
framebuffer_manager.cpp:345 did not run. The color-width stride lead does
not apply: this call's stride is 2048. Do not patch the shader. Do not
change a default. Do not repeat the guest-versus-GPU comparison except as
the control below.

Pixel (x, y) of this image is at 0x00B56000 + y*2048 + x*2. The 0x0000
bytes at x=16, y=180 therefore sit at 0x00BB0020. The 1024x480 depth
texture that enters at all zeros is a different GPU texture. Do not treat
it as 0x00B56000.

ONE work unit, one binary, both widths. Extend the existing copyToRAM
trace. Do not use the phase==4 hash log (ROGUESQ_LOG_G1D_COPY caps at 400
rows and drops earlier phases) as the witness. When ROGUESQ_FLOOR_DEPTH_DIR
is set, every NativeTarget::copyToRAM whose siz is 16-bit and whose width
is 796 or 1024 appends one record from boot, not only phase >= 4:
- phys, width, rowStart, rowEnd
- the rawBe uint16 at x=16 and x=width-17 for each y in 180..192 and for
  y=200, when that row is inside the write
rawBe is the s6626 guest capture's word: 32-bit byteswap of the RDRAM
bytes, then the 16-bit swap, the same path as rs64DepthHistCaptureGuest.
Do not invent a third conversion. Also record the total copyToRAM call
count for every siz, so an empty overlap list is not a dead logger. Keep
the s6626 guest column capture on the state.cpp:2604 upload.

Hypotheses and discriminating outcomes:
- H-writeback: a recorded copyToRAM covers 0x00B56000 + y*2048 + 16*2 for
  y=180..192, and the stored rawBe is 0x0000. Name width, row range, and
  whether another sampled word in that write is 0xFFFC.
- H-later-zero: a recorded write covers those pixels and stored 0xFFFC or
  another nonzero depth word, and the later state.cpp:2604 upload still
  reads rawBe 0x0000.
- H-unwritten: the copyToRAM count is >0 and no record's byte range covers
  those 0x0000 pixels before the upload. Host writeback is not the writer.
  Do not start a guest-store watch in this unit. Name it as the residual.
- H-witness: the copyToRAM count is 0, the upload's guest file is missing,
  the 21:9 clear-then-0x0000 sequence does not recur, or the 16:9 z store
  is absent. Repair the log in this same iteration before interpreting a
  null.

Positive controls, required: magenta pixel (16,180) still changes; 16:9
floor-enter depth stays 1.0 and a later floor op stores z in 0.990..0.998;
the 21:9 upload's rawBe head is 0x0000 on x=16 for y=180..192 and the GPU
match stays max abs 0; copyToRAM count is >0 on both arms. A silent log is
not a result. Phase-gate the route. No cross-run animation compare. Screen
must be unlocked. SIGKILL. One game run at a time. Do not overwrite
scratch/agent/s6624_attachment, scratch/agent/s6625_depth, or
scratch/agent/s6626_guest.

Build and run from build/ with the ROM beside it:

    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp
    python3 tools/g1d_floor_depth.py --output-root scratch/agent/s6627_ram

Keep tools/g1d_floor_depth.py --selftest and tools/g1d_floor_attachment.py
--selftest green. If lib/ changes, ./submodule-patches/export.sh is part
of the commit.
