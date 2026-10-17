#!/bin/zsh
# Lint for the s5229-s5232 class: host code reading guest RDRAM bytes/halfwords
# without the swizzle (rdram[] is word-swapped: byte a lives at rdram[a^3],
# halfword a at a^2). Aligned 32-bit casts/memcpy are fine. Use
# src/main/rs64_rdram_peek.h for probe reads.
# Usage: tools/lint_rdram_reads.sh [--selftest]   (exit 1 on any hit)
cd "${0:A:h}/.." || exit 2
dirs=(src lib/N64ModernRuntime/librecomp/src lib/N64ModernRuntime/ultramodern/src)
scan() {
  # 1) 8/16-bit pointer casts straight off rdram without ^2/^3
  grep -rnE '(u?int16_t|u?int8_t|char)[[:space:]]*\*\)[[:space:]]*\(?[[:space:]]*&?(ctx->)?rdram' "$@" 2>/dev/null | grep -vE '\^[[:space:]]*[23]'
  # 2) hand-composed multi-byte reads from rdram[] without ^3
  grep -rnE 'rdram\[[^]]*\][[:space:]]*<<[[:space:]]*(8|16|24)' "$@" 2>/dev/null | grep -vE '\^[[:space:]]*3|rs64_rdram_peek.h'
}
if [[ "$1" == --selftest ]]; then
  t=$(mktemp -d)
  print -r -- '*(uint16_t*)(rdram + p);' > $t/a.c
  print -r -- 'x = rdram[p]<<8 | rdram[p+1];' > $t/b.c
  n=$(scan $t | wc -l); rm -rf $t
  (( n == 2 )) && { echo "selftest OK (positive control fired $n)"; exit 0; }
  echo "selftest FAIL ($n)"; exit 2
fi
out=$(scan $dirs)
[[ -z $out ]] && { echo "lint_rdram_reads: clean"; exit 0; }
print -r -- "$out"; exit 1
