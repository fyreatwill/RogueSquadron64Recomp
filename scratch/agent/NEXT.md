# NEXT: 21:9 hangar SIGBUS — heap tail vs w1024 image at e4 (s6688)
HYPOTHESIS-ID: g1d-heap-image-overlap
Datum (s6688): 21:9 lvl1 forced route crashes ~2 min in, hangar craft-select, si_addr guest
0x7FFF0002, mallocVoiceLineStruct <- craftSelectionVoiceLineHelper. 5/5 + 1/1 with
ROGUESQ_WINDOW_FIT=0 (not G1f); 16:9 clean. s6631 heapcap did=3 shortens a LIVE block
(fl 0x0006 size 0x14B000) to plant the terminator at e4-0x10; a free-only variant (leave retail
header at e4) still crashed the same way -> both places get overwritten.
Hypotheses:
- H-image: the w1024 colour image (starts at e4) or its RT64 write-back overwrites e4-0x10..e4+0x10.
- H-owner: the live 0x14B000 block's owner (audio/zlib/terrain?) fills its last 16 bytes (0x7FFF = PCM saturation hint).
- H-layout: e4 itself is wrong at 21:9/12 MB (heap should end one header + guard below the image).
Discriminator, ONE build: per heap rebuild log e4, block owner tag of the 0x14B000 block, and
add a cheap per-VI check of the 32 bytes at e4-0x10 that logs the first change (value, VI,
guest PC from the last recompiled func breadcrumb). Which writer changes them selects H-image vs H-owner.
Fix candidate: cap the heap end at e4 - 0x10 - guard by cutting the free block BEFORE the live one,
or move the image up by 0x20. Done = 21:9 forced lvl1 mission_verified_130s, s6631 level-select
check passes, 16:9 unchanged. Then capture the 21:9 G1f window in flight (tools/g1f_window_check.sh).
Recipe: env HOLD_S=150 zsh tools/g1_lvl1_aspect_arm.sh <tag> 21:9 "<extra env>"
Heapcap code lives in tools/apply_s6031_far.py (emitted into N64Recomp/RecompiledFuncs/funcs_0.c;
edit both identically, or rerun the fixup chain).
After that: G3d turning-shake follow-up.
