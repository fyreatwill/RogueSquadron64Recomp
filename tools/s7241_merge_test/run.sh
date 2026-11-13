#!/bin/zsh
# s7241: host unit test for the s7239 WIDEWIN 2x2 merge (rs64_s7239_* in src/main/upstream_compat.cpp).
# Extracts the live block verbatim, drives it with synthetic RDRAM cell lists, emulates the game's flat TRI_GEN
# writer (docs/WIDEWIN-MERGE-PLAN.md fact 2) and decodes the ucode vertices (fact 3). Exit 0 = all cases pass.
set -e
H=${0:A:h}; ROOT=${H:h:h}; O=${TMPDIR:-/tmp}/s7241_merge_test; mkdir -p $O
awk '/^\/\/ s7240 G1c \(tools\/apply_s7239_widewin_merge.py/{f=1} /^extern "C" int rs64_s6882_on/{f=0} f' $ROOT/src/main/upstream_compat.cpp > $O/s7239_block.inc
[[ -s $O/s7239_block.inc ]] || { echo "extract failed"; exit 1; }
clang++ -std=c++17 -O1 -g -fsanitize=address,undefined -I$O -o $O/t $H/test.cpp
$O/t
