#!/bin/zsh
# s7584: runtime uninitialized-read witness (class UI). Builds $B (default build_autoinit) with every C and C++ TU compiled
# -ftrivial-auto-var-init=$INIT (pattern = 0xAA.. fill, zero = 0 fill), at each target's real optimisation (CMakeLists
# per-target -O2). C TUs also force-include tools/s7578_ubsanc_plant.h (control ROGUESQ_S7578_PLANT=7: prints an uninitialized
# local and a fresh malloc word; pattern arm + MallocPreScribble=1 must print 0xAAAAAAAA for both).
# Heap side needs no rebuild: run with MallocScribble=1 (libmalloc fills new blocks 0xAA, freed 0x55; controlled by plant 7 in-game).
# The plant reads the malloc word through volatile: a plain load of fresh malloc memory is folded to undef at -O2 (first s7584 try).
# Usage: env INIT=pattern B=build_autoinit zsh tools/build_autoinit.sh ; run from $B with the ROM beside it.
set -e
cd "${0:A:h}/.."
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
B=${B:-build_autoinit}; INIT=${INIT:-pattern}
cmake -S . -B $B -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DCMAKE_C_FLAGS_DEBUG="-g -ftrivial-auto-var-init=$INIT -include $PWD/tools/s7578_ubsanc_plant.h" \
  -DCMAKE_CXX_FLAGS_DEBUG="-g -ftrivial-auto-var-init=$INIT" -DCMAKE_OBJCXX_FLAGS_DEBUG="-g -ftrivial-auto-var-init=$INIT"
cmake --build $B -j"${JOBS:-10}"
ln -sf "$PWD/rogue_squadron.z64" $B/rogue_squadron.z64 2>/dev/null || true
# The forced-level route needs a profile: COPY (never move) the owner's save into this dir; build/saves is untouched.
mkdir -p $B/saves; [[ -s $B/saves/rs64.n64.us.1.0.bin ]] || cp -p build/saves/rs64.n64.us.1.0.bin* $B/saves/
for z in build/*.z64; do ln -sf "$PWD/$z" $B/ 2>/dev/null || true; done
# Flag census: every compile command must carry the init flag (C and C++), printed as total/with.
python3 - "$B" "$INIT" <<'PY'
import json,sys
cc=json.load(open(sys.argv[1]+'/compile_commands.json')); f='-ftrivial-auto-var-init='+sys.argv[2]
for lang,ext in (('c',('.c',)),('cxx',('.cpp','.cc','.cxx')),('objcxx',('.mm',))):
    rows=[r for r in cc if r['file'].endswith(ext)]; w=[r for r in rows if f in r.get('command','')+' '.join(r.get('arguments',[]))]
    print(f"[s7584-flags] {lang} tus={len(rows)} with_flag={len(w)}")
PY
# Configuring a second build dir drops build/'s spirv-cross subproject rules (s5598, s7354); regenerate them so build/ stays green.
cmake -S . -B build > /dev/null
