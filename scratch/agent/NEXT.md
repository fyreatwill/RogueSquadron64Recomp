# NEXT: 21:9 hangar SIGBUS — who makes the voice-list pointer 0x7FFF0000 (s6689)
HYPOTHESIS-ID: g1d-hangar-voice-ptr
Datum (s6689): mallocVoiceLineStruct(a0=0x7FFF0000) — lhu 0(a0) with ^2 swizzle -> si_addr
0x7FFF0002. Caller craftSelectionVoiceLineHelper (0x800AE264, funcs_28.c):
  idx  = byte[0x800CD6E8]; s1 = byte[0x800CC404 + idx]
  gate: word[0x800CDA18]==0, byte[0x800CDA08 + s1-1]==0
  a0   = word[0x800CC4F8 + (s1-1)*4]
4/4 crash at 21:9 with the s6689 heapslot fix (heap no longer on the depth image); 16:9 clean.
Hypotheses:
- H-index: s1 is 0 or past the table at 21:9 (index from a wide-only code path, e.g. hangar
  cursor/craft slot driven by screen x) -> table intact, no writer.
- H-overwrite: a store or DMA (RT64 write-back, zlib, carve-moved buffer) writes the table at
  0x800CC4F8.. or the index bytes.
Discriminator, ONE build already exists (ROGUESQ_FLOOR_WATCH, s6689): run both widths with
  ROGUESQ_FLOOR_DEPTH_DIR=<abs dir> ROGUESQ_FLOOR_WATCH=0x0CC4F4,0x0CC4F8,0x0CC4FC,0x0CC500,0x0CD6E8,0x0CDA18
  env HOLD_S=150 zsh tools/g1_lvl1_aspect_arm.sh v21 21:9 "<env>"   then same with 16:9.
Writers in rdram.jsonl (k=writer, target in watch) + values at crash. If no writer touches the
table and values match 16:9 -> H-index: also add a one-shot fprintf in the helper via a fixup
(s1, idx, a0) to read the index at the crash. Fix at the root (the wide path that yields the index
or the overwriting writer). Also re-run the s6631 level-select tear check with heapslot.
Then the 21:9 G1f window capture (tools/g1f_window_check.sh), then G3d turning-shake.
