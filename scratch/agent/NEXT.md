# NEXT: what Start-in-hangar changes so the odd-DMA node field reads ASCII 0x6C637265
HYPOTHESIS-ID: m5-audio-destub
Established (s4566, single run per arm): arm A (mash) reaches the hangar, then odd DMA phys=0x1C637265 (guest 0x6C637265) ram=0x8019CF90 len=0x300; arm B (mash stops at first 512) sits in the hangar with 0 crashes and 0 odd DMAs.
Hypotheses: H-string-node (mission-load code reads a node whose cart field is a name string), H-heap-clobber (audio/heap corruption family), H-retail-same (retail issues it too; needs oracle).
Discriminator: first fix the s4298 scan in lib/N64ModernRuntime/librecomp/src/pi.cpp to compare the GUEST word 0x6C637265 (it compares the physical word, so it always reports hits=0), then rerun with a single Start press vs mash and name the node and its writer. A lib edit needs submodule-patches/export.sh and a commit in the same session.
