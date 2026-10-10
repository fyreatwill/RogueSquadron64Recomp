#!/bin/zsh
# Build the rdplog video plugin against the oracle's mupen64plus-core API headers.
cd "$(dirname "$0")"
API=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/api
cc -O2 -dynamiclib -fvisibility=default -I$API -o rdplog.dylib rdplog.c
