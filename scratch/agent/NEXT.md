# Next work unit: dump data referenced by hangar child DLs (VI 512 task0)

HYPOTHESIS-ID: hangar-artifact-triage

s4510: root + all 13 child DLs are structurally identical retail vs port (only working-buffer pointers differ). Remaining: H2' guest vertex/texture/matrix DATA differs vs H1/H3 renderer/ucode with identical data.
Do: in both dump hooks, parse each task0 child (parser in scratch/agent/s4509_dlparse.py / s4510_cmp.py), collect op 04 (vertex) w1 pointers + length, fd/f5 texture pointers, 01 matrix pointers, dump 0x400 B at each; compare retail vs port content (same buffer set = task0). Start with c05 +0xB0 target (0x806F3A10 retail vs 0x80718A10 port).
Outcomes: identical data => renderer/H1/H3 (compare RDP output/ucode path); differing data => trace writer of that data (H2').
Scripts: scratch/agent/s4510_oracle.sh, s4510_port.sh (RS64_GFX_DL_DUMP_DIR). Build: DEVELOPER_DIR=... cmake --build build -j8; tools/oracle/build.sh.
