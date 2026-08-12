# Blocked: alternate Mupen64Plus RSP plugin

Need: a compatible macOS Mupen64Plus RSP dylib and its filesystem path.

From: a human who can supply or install that plugin.

Tried: on 2026-08-12, an inventory of `/opt/homebrew` and `/usr/local` found
only `/opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-rsp-hle.dylib`.
The current HLE arm alone stays at VI width 320 even while PIF injection and
whole-RDRAM write controls fire. A paired alternate/current 70-second run is
the single discriminator: alternate reaches 640/1024/hangar means the HLE RSP
route is responsible; both remain at 320 means the core/debugger environment
is responsible.

When supplied, use the two exact commands in `scratch/agent/NEXT.md`.
