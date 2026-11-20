#!/bin/zsh
# SOAK_NEEDS_IDLE=300
# s7704 G1d 21:9: does RT64's skip of the 768-wide colour write-back (SKIP_WILD_W) change the PICTURE in the boot cinematic,
# where the game LOADBLOCKs its previous frame (s7702: 0x9B6000 / 0xA35800, t 12.0-16.7 s)?
# Arms (sequential, presented frames by ScreenCaptureKit, plain boot, owner-ish recipe FPS60 dd2):
#   skip   21:9 default (write-back skipped)                      <- what the owner gets
#   wb     21:9 ROGUESQ_ALLOW_WILD_W=1 (write-back done)           <- H-gpu: same picture as skip; H-stale: differs
#   rdram  21:9 ROGUESQ_FBOVL_SKIP=1 (RT64 ignores its GPU fb for loads in the window, TMEM gets RDRAM bytes) <- positive
#          control: this arm MUST differ from skip in the copied region, or the picture instrument cannot see the copy
#   rdwb   21:9 FBOVL_SKIP=1 + ALLOW_WILD_W=1 (RDRAM path with the write-back present): retail-like reference of the RDRAM route
#   pskip  21:9 ROGUESQ_S7704_POISON=768: magenta fill of the 768 rows before the (skipped) write-back <- the real positive control:
#          if the copied buffer can reach the screen at all, magenta shows here
#   pwb    POISON=768 + ALLOW_WILD_W=1: the write-back overwrites the fill <- must look like wb (fill does not leak)
#   r43    4:3 default (640 buffers, write-back allowed)          <- reference that the copy shows at 4:3
# Every arm logs ROGUESQ_LOG_FBOVL in the read window so the log says whether RT64 resolved the loads to a GPU framebuffer.
# Score: tools/s7704_fbcopy_score.py. Owner save read-only (NO_SAVE_WRITE), cmp-checked.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 2; }
O=${O:-$PWD/scratch/s7704}; SV=build/saves/rs64.n64.us.1.0.bin; mkdir -p $O
cp -p $SV $O/save_before.bin || exit 3
SECS=${SECS:-24}
WIN="ROGUESQ_LOG_FBOVL=1 ROGUESQ_FBOVL_LO=9B6000 ROGUESQ_FBOVL_HI=AC0000 ROGUESQ_FBOVL_CAP=4000"
for arm in ${=ARMS:-skip wb rdram rdwb r43}; do
  case $arm in
    skip)  X="ROGUESQ_ASPECT=21:9"; CW=672; CH=288;;
    wb)    X="ROGUESQ_ASPECT=21:9 ROGUESQ_ALLOW_WILD_W=1"; CW=672; CH=288;;
    rdram) X="ROGUESQ_ASPECT=21:9 ROGUESQ_FBOVL_SKIP=1"; CW=672; CH=288;;
    rdwb)  X="ROGUESQ_ASPECT=21:9 ROGUESQ_FBOVL_SKIP=1 ROGUESQ_ALLOW_WILD_W=1"; CW=672; CH=288;;
    pskip) X="ROGUESQ_ASPECT=21:9 ROGUESQ_S7704_POISON=768"; CW=672; CH=288;;
    pwb)   X="ROGUESQ_ASPECT=21:9 ROGUESQ_S7704_POISON=768 ROGUESQ_ALLOW_WILD_W=1"; CW=672; CH=288;;
    r43)   X="ROGUESQ_FBOVL_LO=A20000"; CW=384; CH=288;;
  esac
  ( cd build && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=2 ${=WIN} ${=X} \
      ./RogueSquadron64Recomp ) > $O/$arm.log 2>&1 &
  P=$!; sleep 1
  scratch/s6894/g5b_capture RogueSquadron64Recomp $O/$arm.raw $CW $CH 0 $SECS > $O/cap_$arm.txt 2>&1 &
  c=$!; sleep $((SECS + 2))
  a=1; kill -0 $P 2>/dev/null || a=0
  kill -9 $P 2>/dev/null; wait $c 2>/dev/null; wait $P 2>/dev/null
  echo "tag=fbcopy_$arm alive=$a crash=$(grep -a -c -E 'CRASH|SIGSEGV|SIGBUS|abort' $O/$arm.log) fbovl=$(grep -a -c '^\[fbovl\] tex' $O/$arm.log) skipw=$(grep -a -c 'SKIP_WILD_W' $O/$arm.log) poison=$(grep -a -c "s7704-poison" $O/$arm.log) frames=$(sed -n 's/^frames \([0-9]*\).*/\1/p' $O/cap_$arm.txt)"
done
cmp -s $SV $O/save_before.bin && echo save-unchanged || { echo SAVE-CHANGED; exit 5; }
