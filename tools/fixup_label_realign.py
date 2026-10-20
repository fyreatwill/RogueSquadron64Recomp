"""s5668: repair N64Recomp's lagging-label bug (src/recompilation.cpp:874 emits at most ONE label per
instruction, so any out-of-function / junk branch target in the sorted label set delays every later real label).
Symptom: `goto L_8009DD8C` lands on a different instruction than the `// 0x8009DD8C:` comment says
(audioCompandS16 returned +-0x7FFF for every input -> the voice-audio noise layer).
Repair, per function that has a misplaced label: drop every label line whose address differs from the
next 4-space instruction comment, then place `L_<addr>:` before the 4-space `// 0x<addr>:` line for every
address that some `goto` in the function still references. Idempotent. Run after fixup_game_funcs.py.
usage: fixup_label_realign.py <RecompiledFuncs dir> [--dry]"""
import re, sys, glob
LBL = re.compile(r'^(L_([0-9A-F]{8})):\s*$')
CMT = re.compile(r'^    // 0x([0-9A-F]{8}):')
GOTO = re.compile(r'\bgoto (L_[0-9A-F]{8});')
FN = re.compile(r'^RECOMP_FUNC void (\w+)')
def fix_function(lines):
    mis = False
    for i, l in enumerate(lines):
        m = LBL.match(l)
        if m:
            for j in range(i + 1, min(i + 4, len(lines))):
                c = CMT.match(lines[j])
                if c:
                    if c.group(1) != m.group(2): mis = True
                    break
    if not mis: return lines, 0, []
    body = "\n".join(lines)
    targets = set(GOTO.findall(body))
    addrs = {m.group(1) for m in map(CMT.match, lines) if m}
    out, kept = [], set()
    for i, l in enumerate(lines):
        m = LBL.match(l)
        if m:
            nxt = next((CMT.match(x) for x in lines[i + 1:i + 4] if CMT.match(x)), None)
            if nxt and nxt.group(1) == m.group(2): kept.add(m.group(1)); out.append(l)
            elif m.group(1) in targets and m.group(2) not in addrs: out.append(l)  # dead out-of-function target: keep so goto still compiles
            continue
        out.append(l)
    res, placed = [], set()
    for l in out:
        c = CMT.match(l)
        if c:
            lab = "L_" + c.group(1)
            if lab in targets and lab not in kept and lab not in placed:
                res.append(lab + ":"); placed.add(lab)
        res.append(l)
    missing = sorted(t for t in targets if t not in kept and t not in placed)
    return res, len(placed), missing
def main():
    d = sys.argv[1]; dry = "--dry" in sys.argv
    for f in sorted(glob.glob(d + "/funcs_*.c")):
        L = open(f).read().split("\n"); out = []; i = 0; changed = False
        starts = [k for k, l in enumerate(L) if FN.match(l)] + [len(L)]
        out.extend(L[:starts[0]])
        for a, b in zip(starts, starts[1:]):
            new, n, missing = fix_function(L[a:b])
            if new is not L[a:b] and new != L[a:b]:
                changed = True
                print(f"{f.split('/')[-1]} {FN.match(L[a]).group(1)}: placed {n} labels; goto targets with no instruction: {missing}")
            out.extend(new)
        if changed and not dry: open(f, "w").write("\n".join(out))
main()
