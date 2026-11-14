#!/bin/zsh
# s7362 class AM two-arm control: pre bucketlog rd() reads host memory 2 GB below rdram, post reads the guest word.
set -e
cd "${0:A:h}/.."
c++ -std=c++17 -O1 -o /tmp/s7362_rawneg_ctl tools/s7362_rawneg_ctl.cpp
/tmp/s7362_rawneg_ctl
