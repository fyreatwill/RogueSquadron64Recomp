# NEXT: 21:9 level-select tear: where is the 1024-wide depth clear lost?
HYPOTHESIS-ID: g1d-levelselect-rt64-depth

s6693 census (scratch/agent/s6693_depthrl, ab.py; fc/ subdir for fast-clear arms): at 21:9 the depth
fb 00B56000 is always h=339 lastWriteType=Depth diff=0 in fullSync; at 16:9 the 796 fb is h=340 lwt=Color
diff=1 (clear copied colour->depth each frame). Reload kill-switches only modulate; NO_DEPTH_FASTCLEAR no effect.

Hypotheses:
- H-cimg: at 21:9 the clear pair's cimg differs (width != 1024, or address != 00B56000, e.g. 00B55FFx),
  so get() keys/sizes it elsewhere. Then the draw pair's depth fb never sees it.
- H-manager: the clear is applied only in the workload-queue fbManager (as type Depth via the fast path, or
  as Color), and the state-thread manager used by fullSync never learns it. That is harmless at 16:9 only
  because the 16:9 pairs take fullSync for the clear pair too.
- H-skip: the clear pair is dropped (drawColorRect empty or flushed) before submitFramebufferPair at 1024.
Discriminator (one build, one 21:9 + one 16:9 run): under ROGUESQ_LOG_DEPTH_PAIR, also log every pair with
fillRectOnly=1 in submitFramebufferPair (cimg addr/width/siz/rect, clearDepthOnly) and in fullSync
getFramebufferPairs (whether reached, colorFb addr/h/lwt after the write), keyed by submissionFrame.
Clear pair at 21:9 with a different addr/width -> H-cimg; reaches submit but not fullSync -> H-manager;
absent from submit -> H-skip. Positive control: 16:9 clear pair shows up in both and sets lwt=Color.
Then fix the cause and score 21:9 level-select with g1d_row_noise (target vhf < 7). Send the owner the
before/after frames. After that: G3d turning-shake.
