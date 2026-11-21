#!/bin/zsh
# s7751: build the cxd4 task replay (scalar C VU, no SSE/NEON) into tools/s7751_cxd4_task/replay.
set -e
H=${0:A:h}; C=${CXD4:-$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4}; A=${C:h}/mupen64plus-core/src/api
cc -O2 -w -DM64P_PLUGIN_API -I$C -I$A -o $H/replay $H/replay.c $C/osal_dynamiclib_unix.c
echo built $H/replay
