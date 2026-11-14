#!/bin/zsh
# s7361 class AL control: pre text faults past the 4 GB rdram reservation, post text reads the planted guest word.
cd "${0:A:h}/.." || exit 1
mkdir -p scratch/s7361
clang++ -std=c++20 -O0 -w -Ilib/N64ModernRuntime/N64Recomp/include tools/s7361_zext_ctl.cpp -o scratch/s7361/zext_ctl || exit 1
scratch/s7361/zext_ctl
