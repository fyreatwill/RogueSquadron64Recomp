#!/bin/sh
# s7575: compile one RecompiledFuncs file to -O2 IR (RecompiledFuncs -O2 flags: tools/s7575_ir_flags.txt; run from repo root) and list surviving do_break vram args.
# Run: mkdir -p D; ls ../N64Recomp/RecompiledFuncs/funcs_*.c | env D=D xargs -P6 -n1 sh tools/s7575_ir_calls.sh
b=$(basename "$1" .c); D=${D:-scratch/s7575/ir}
clang $(cat tools/s7575_ir_flags.txt) -S -emit-llvm -o $D/$b.ll "$1" 2>/dev/null
grep -o 'call void @do_break(i32 noundef -*[0-9]*)' $D/$b.ll | grep -o -- '-*[0-9]*)' | tr -d ')' > $D/$b.calls
: > $D/$b.ll
