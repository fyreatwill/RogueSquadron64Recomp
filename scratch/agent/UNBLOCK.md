# UNBLOCK s4778 — route 1 (refuted)

Block claimed: mapping musyxSynthFrame_s4562_impl+5808 needs lldb/objdump approval.
Refutation: the build is CMake/Makefiles, whose allowed `make` has a per-TU assembly target:
`cd build && make Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c.s`
(output under build/CMakeFiles/RecompiledFuncs.dir/.../funcs_24.c.s, same flags as the real object, -O0 so arm64 is 4 B/insn).
Counting instructions from `_musyxSynthFrame_s4562_impl:` to byte 5808 gives `ldrh w8,[x8,x9]` with
`.loc funcs_24.c:7112` = guest `0x80091368: lhu $v0,0x10($v1)` (label L_80091368).
Result: x9 = ((r3+0x10)^2)+0x80000000 = 0x8000950e => (r3+0x10)^2 = 0x950e => guest $v1 = 0x94FC,
a small non-pointer. Loop 0x80091368..0x80091380 walks a linked list (v1 = lw 0(v1) until 0), so a node's next
pointer (or the head) holds 0x94FC. Hypothesis A (macro lacks mask) refuted: MEM_H adds 0x80000000 by design;
the guest value itself is bad. B (corrupt list node) is the live one. Single-source (static mapping).
