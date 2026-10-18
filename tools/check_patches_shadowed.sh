#!/bin/zsh
# Reports whether each function PatchesLib defines is ALSO defined by
# libRecompiledFuncs.a. On macOS ld64 an archive member is only pulled in to
# satisfy an undefined reference, so a patch whose symbol is already defined by
# an earlier-resolved RecompiledFuncs object is silently never linked
# (s5366: allocateDisplayListBuffer). Usage: tools/check_patches_shadowed.sh [build_dir]
BUILD=${1:-${0:A:h:h}/build}
shadowed=0
for sym in $(nm -g "$BUILD/libPatchesLib.a" 2>/dev/null | awk '$2=="T"{print $3}'); do
  if nm -g "$BUILD/libRecompiledFuncs.a" 2>/dev/null | awk -v s="$sym" '$2=="T" && $3==s{f=1} END{exit !f}'; then
    echo "SHADOWED: $sym is defined in libRecompiledFuncs.a too (patch member likely not linked)"
    shadowed=$((shadowed+1))
  else
    echo "unique:   $sym"
  fi
done
echo "shadowed=$shadowed"
[ $shadowed -eq 0 ]
