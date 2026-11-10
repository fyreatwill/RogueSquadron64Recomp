#!/bin/zsh
# s7098: build frame_replay against a 16 MB angrylion-plus core. The stock g3_angrylion build has RDRAM_MAX_SIZE 0x800000
# (n64video.h), and rdp/rdram.c sizes its static rdram_hidden[] array from it. At dd>1 the game puts colour/Z images above
# 8 MB (s7098 L6 dd4 16:9: cimg 0x98AA00), so the stock core overflows that global (ASan: fbfill_16 global-buffer-overflow)
# and SIGSEGVs. Any replay of a dd>1 frame with an image above 8 MB was invalid on the old build.
# usage: build16.sh <outdir>   -> <outdir>/frame_replay16  (copies the core source to <outdir>/alp, patches, builds -O2)
set -e
O=${1:?outdir}; R=${0:A:h}; S=~/Documents/Tools/g3_angrylion/src/src
mkdir -p $O; rm -rf $O/alp; cp -R $S $O/alp
sed -i '' 's/#define RDRAM_MAX_SIZE 0x800000/#define RDRAM_MAX_SIZE 0x1000000/' $O/alp/core/n64video.h
grep -q 'RDRAM_MAX_SIZE 0x1000000' $O/alp/core/n64video.h
A=$O/alp
clang -O2 -w -I$A/core -I$A -c $A/core/n64video.c -o $O/n64v16.o
clang++ -std=c++14 -O2 -I$A/core -I$A -c $A/core/parallel.cpp -o $O/par16.o
clang -O2 -I$A/core -I$A $R/frame_replay.c $O/n64v16.o $O/par16.o -lc++ -o $O/frame_replay16
echo built $O/frame_replay16
