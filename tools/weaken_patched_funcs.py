#!/usr/bin/env python3
"""Mark RecompiledFuncs definitions weak for functions a C patch overrides.

macOS ld64 only pulls an archive member to satisfy an undefined reference, so a
PatchesLib override of a symbol that libRecompiledFuncs.a also defines is never
linked (s5366, tools/check_patches_shadowed.sh). A weak definition in
RecompiledFuncs lets the strong PatchesLib one win. Run AFTER
fixup_game_funcs.py (regen order: make_elf -> N64Recomp -> fixup -> THIS ->
cmake). Only names in PATCH_WEAKEN are touched: a function whose body carries
hand fixups (e.g. allocateDisplayListBuffer) must stay shadowed.

usage: weaken_patched_funcs.py RECOMPILED_FUNCS_DIR
"""
import re
import sys
from pathlib import Path

PATCH_WEAKEN = ["isCinematicActive", "setRngSeed"]  # s6269 qualification probe

def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    changed = 0
    for path in sorted(Path(sys.argv[1]).glob("funcs_*.c")):
        text = path.read_text()
        new = text
        for name in PATCH_WEAKEN:
            pat = re.compile(r"^RECOMP_FUNC void %s\(" % re.escape(name), re.M)
            new = pat.sub("__attribute__((weak)) RECOMP_FUNC void %s(" % name, new)
        if new != text:
            path.write_text(new)
            changed += 1
            print(f"weakened in {path.name}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
