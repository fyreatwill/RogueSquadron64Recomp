#!/bin/zsh
# s7151: build tools/g5b_capture.swift into the path the s714x arms use (scratch/s6894/g5b_capture). Captures are sRGB at
# source since s7151 (G5B_CS=native restores the old Display-P3-untagged output). The pre-s7151 binary is kept beside it.
# NOTE: two processes of the SAME executable path both hang in the SCK window lookup (s7151, measured twice): copy the
# binary for a second concurrent capture (tools/s7151_arm.zsh does).
cd "$(git rev-parse --show-toplevel)"
O=scratch/s6894/g5b_capture; mkdir -p scratch/s6894
[ -f $O ] && [ ! -f ${O}_pre7151 ] && cp -p $O ${O}_pre7151
swiftc -O tools/g5b_capture.swift -o $O && echo built $O
