#!/bin/zsh
# s7578: runtime signed-overflow witness for the GENERATED GAME C. Builds build_ubsanc/ (separate from build/): every C TU
# (RecompiledFuncs at its real -O2) gets -fsanitize=signed-integer-overflow (recoverable) and force-includes
# tools/s7578_ubsanc_plant.h (control: ROGUESQ_S7578_PLANT=1). C++ is built as in build/. build_asan never instrumented
# the generated C (s7467: C++ only), so this is the first runtime UB witness for it.
# Run from build_ubsanc/ with the ROM beside it; UBSAN_OPTIONS=halt_on_error=0:log_path=<p>.
set -e
cd "${0:A:h}/.."
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
B=${B:-build_ubsanc}
# s7579: SAN selects the sanitizer list (default s7578 signed overflow); e.g. SAN=bounds,signed-integer-overflow B=build_ubsanb.
SAN=${SAN:-signed-integer-overflow}
# s7583: SANREC = recoverable subset (unreachable/return cannot be recovered); defaults to SAN.
SANREC=${SANREC:-$SAN}
cmake -S . -B $B -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_C_FLAGS_DEBUG="-g -fsanitize=$SAN -fsanitize-recover=$SANREC -include $PWD/tools/s7578_ubsanc_plant.h" \
  -DCMAKE_EXE_LINKER_FLAGS="-fsanitize=undefined"
cmake --build $B -j"${JOBS:-10}"
ln -sf "$PWD/rogue_squadron.z64" $B/rogue_squadron.z64 2>/dev/null || true
# The forced-level route needs a profile: COPY (never move) the owner's save into this dir; build/saves is untouched.
mkdir -p $B/saves; [[ -s $B/saves/rs64.n64.us.1.0.bin ]] || cp -p build/saves/rs64.n64.us.1.0.bin* $B/saves/
for z in build/*.z64; do ln -sf "$PWD/$z" $B/ 2>/dev/null || true; done
# Configuring a second build dir drops build/'s spirv-cross subproject rules (s5598, s7354); regenerate them so build/ stays green.
cmake -S . -B build > /dev/null
