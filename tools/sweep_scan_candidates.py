"""Generated-symbol renaming sweep: find TOML function placeholders
that already have a real name in the generated N64Recomp tree.

Usage: python3 tools/sweep_scan_candidates.py <start_name>
<start_name> is the TOML entry to resume the scan from
(inclusive), e.g. fake_func_800E406C.

Walks syms/rogue_squadron.syms.toml in file order (NOT sorted by address —
overlay sections reuse VRAM ranges) starting at <start_name>, and for each
subsequent func_8xxxxxxx entry looks up its generated .c definition. Stops
at the first entry that either has no generated definition, is still a
placeholder itself, or whose address has more than one RECOMP_FUNC-prologued
match across the generated tree (overlay VRAM reuse — needs manual review,
never silently resolved from the first match).
"""
import re, glob, sys

GEN_DIR = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs"
TOML = "syms/rogue_squadron.syms.toml"

if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} <start_name e.g. func_800FFE00>", file=sys.stderr)
    sys.exit(1)
start_name = sys.argv[1]

# Build addr -> [(generated_name, file, lineno), ...] by scanning for
# "// 0xADDR:" comment lines and checking the RECOMP_FUNC line 3 above.
# Overlay VRAM ranges can be reused by other overlays, so record EVERY
# qualifying match per address and flag collisions instead of silently
# keeping the first one.
addr_to_matches = {}
files = sorted(glob.glob(GEN_DIR + "/funcs_*.c"))
comment_re = re.compile(r'^\s*// 0x([0-9A-Fa-f]{8}):')
func_re = re.compile(r'^RECOMP_FUNC void (\w+)\(')

for fp in files:
    with open(fp, errors="replace") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        m = comment_re.match(line)
        if not m:
            continue
        addr = m.group(1).upper()
        # function start line should be 3 lines above the first comment
        # for that function (RECOMP_FUNC / hi,lo,result / c1cs / comment)
        j = i - 3
        if j >= 0:
            fm = func_re.match(lines[j])
            if fm:
                addr_to_matches.setdefault(addr, []).append((fm.group(1), fp, j + 1))

collisions = {a: m for a, m in addr_to_matches.items() if len(m) > 1}
if collisions:
    print(f"NOTE: {len(collisions)} addresses have multiple RECOMP_FUNC matches "
          f"tree-wide (overlay reuse) — excluded from auto-resolve", file=sys.stderr)

addr_to_name = {a: m[0] for a, m in addr_to_matches.items() if len(m) == 1}

# ordered list of placeholder names from TOML starting at start_name
names = []
with open(TOML) as f:
    for line in f:
        m = re.search(r'name = "((?:fake_func_|func_)?8[0-9A-F]+)"', line)
        if m:
            names.append(m.group(1))

if start_name not in names:
    print(f"error: {start_name} not found in {TOML}", file=sys.stderr)
    sys.exit(1)

ordered = names[names.index(start_name):]

resolved = []
for n in ordered:
    addr = n.rsplit("_", 1)[-1].upper()
    if addr in collisions:
        print(f"STOP: {n} address has multiple overlay matches, needs manual review", file=sys.stderr)
        break
    entry = addr_to_name.get(addr)
    if entry is None:
        print(f"STOP: {n} has no comment/prologue match in generated tree", file=sys.stderr)
        break
    gen_name, fp, lineno = entry
    if gen_name == n or gen_name.startswith(("func_", "fake_func_")):
        print(f"STOP: {n} generated name is still a placeholder ({gen_name}) at {fp}:{lineno}", file=sys.stderr)
        break
    resolved.append((n, gen_name, fp, lineno))

print(f"Resolved {len(resolved)} entries before stopping", file=sys.stderr)
for n, gen_name, fp, lineno in resolved:
    print(f"{n}\t{gen_name}\t{fp}:{lineno}")
