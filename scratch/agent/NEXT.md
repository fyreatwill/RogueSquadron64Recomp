# NEXT work unit (s1666)

HYPOTHESIS-ID: external-retail-entry-boundary

Mandatory REVISIT. After s1665 the last-15 ledger titles (s1651–s1665) are
all sweep-scoped, so do not resume the generated-symbol census. Re-attempt
the external retail-entry boundary with a genuinely new angle: identify the
640 B-frontend after it arrives, and test later inputs ON that frontend.

s1650 already classified A/Start/Z pressed at 75/82/89/96 — those land in
the post-B 1024 intermediate (`512→1024` ~65 s; `1024→640` ~96 s). A/Start
cancelled back to hangar 512; Z was ignored. Only a single Z at ~97.3 s
touched the 640 frontend. Do not repeat that 75–96 s window. Hold/A/B/Z
on hangar, valid D-pad, and post-viewer C/L/R are also parked.

Competing hypotheses and discriminator:

- H1: a later input on the arrived 640 B-frontend (`1024→640` ~96 s,
  origin `0x00696100`) reaches mission PC `0x80000B70`.
- H2: the 640 B-frontend is an already-classified frontend (viewer
  `0x800C9BF0` or hangar `runHangarSelectionFrame`) and later inputs are
  consumed without mission entry or VI-route change.
- H3: the 640 B-frontend is a distinct frontend; later inputs change the
  route (VI/origin/PC) without mission entry.
- H4: the recipe is unevaluable (whole-RDRAM/PIF/VI controls fail, or the
  640 B-frontend is not reached before candidate presses).

Discriminator: one four-arm Rice comparison. Hold completes B-route and
dwells on 640. Candidate arms wait until after `1024→640`, then press
A/Start/Z at 105/115/125/135. Compare VI transitions, origin, pad words,
and watched PCs in the same run.

Exact commands (copy `scratch/agent/s1650_broute_post_controls/run_all.sh`
and change only OUT, `--secs`, and the candidate press times):

```sh
# from repo root; four concurrent arms; ~160 s wall each
ORACLE=tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
ELEVEN=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
B_ROUTE="$ELEVEN,55:b,58:b,63:b"
PCS=0x800AAD9C,0x800AB0EC,0x800AB1C4,0x800B47D0,0x800C58A0,0x800C6854,0x80000B20,0x80000BA8,0x80000BE8,0x80000B70,0x800C9BF0

# arms:
#   hold  --press "$B_ROUTE" --secs 160
#   a     --press "$B_ROUTE,105:a,115:a,125:a,135:a" --secs 160
#   start --press "$B_ROUTE,105:start,115:start,125:start,135:start" --secs 160
#   z     --press "$B_ROUTE,105:z,115:z,125:z,135:z" --secs 160
# common flags:
#   --video "$VIDEO" --watch-write 0x0:0x800000 --hit-cap 10000
#   --watch-write 0x130B10:0x130B58 --watch-write 0x13B40:0x13B48
#   --detail-watch 1 --detail-watch 2 --watch-pc "$PCS"
#   --vi-trace --vi-poll --pif-trace
```

Expected splits:

- H1: any arm shows mission PC `0x80000B70` after a post-arrival press.
- H2: 640 origin stays `0x00696100`; watched PCs are hangar or viewer;
  candidate pads deliver but VI/route match hold.
- H3: post-arrival press changes VI/origin/PC away from hold's 640
  dwell without mission PC.
- H4: whole-RDRAM control misses 10,000 callbacks, B pad `0x40000000`
  is missing, or hold never reaches `1024→640` at `0x00696100`.

Do not start a sweep census this iteration. After this revisit, the next
sweep candidate is `func_800C8178` / `spawnNpcDestructionEffect`.
