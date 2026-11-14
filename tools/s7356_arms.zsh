#!/bin/zsh
# s7356 class AG regression arms: forced host calloc failure at a named site via tools/s7356_failalloc.c (DYLD interpose).
# ctl (S7356_FAIL_IN=__none__) must boot (alive at 15 s); fail (init_overlays) must print "[s7356] FATAL init_overlays" (fixed)
# instead of the pre-fix SIGSEGV si_addr=0x8.  usage: zsh tools/s7356_arms.zsh [site-substring]
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
clang -dynamiclib -O1 -o scratch/s7356/libfailalloc.dylib tools/s7356_failalloc.c || exit 1
cd build
arm(){ ( env ROGUESQ_NO_PKILL=1 ROGUESQ_LOG_PHASE=1 DYLD_INSERT_LIBRARIES=../scratch/s7356/libfailalloc.dylib S7356_FAIL_IN=$2 ./RogueSquadron64Recomp > ../scratch/s7356/$1.log 2>&1 & echo $! > ../scratch/s7356/$1.pid; wait ) &
  sleep 15; P=$(cat ../scratch/s7356/$1.pid); ps -p $P >/dev/null && st=alive || st=exited; kill -9 $P 2>/dev/null; sleep 1
  echo "$1 $st fatal=$(grep -a -c '\[s7356\] FATAL' ../scratch/s7356/$1.log) segv=$(grep -a -c 'caught signal 11' ../scratch/s7356/$1.log)"; }
arm arm_ctl __none__; arm arm_fail ${1:-init_overlays}
