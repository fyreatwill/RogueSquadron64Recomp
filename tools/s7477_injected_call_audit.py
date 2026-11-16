#!/usr/bin/env python3
"""s7477 class EE audit: port PATCH blocks that call a function taking (rdram, ctx) from inside generated code.

A call injected into a generated body can overwrite guest registers the surrounding generated code still reads
(s7476: the s4889 dereg patch saved only $a0, findAndZeroTableSlotMatching reused $a1 as its loop index, and the
MusyX voice count 17 became 1). For every PATCH line that calls `f(rdram, ctx)`:
  clob   = registers f writes, transitively through its own (rdram, ctx) callees (generated or host helper body)
  live   = registers the caller reads after the patch before writing them (worklist over fallthrough + gotos,
           stopping at return and at any later guest call for caller-saved regs other than call arguments)
  rest   = registers the patch line itself writes after its last injected call (save/restore)
  BUG    = clob & live - rest.
Positive control: the pre-s7476 s4889 text (OLD_CALL from tools/apply_s4889_first_dereg.py) must be flagged
with r5 live, and the current text must pass.
Usage: s7477_injected_call_audit.py [RecompiledFuncs dir]   (exit 1 if any BUG, 3 if the control fails)
"""
import re, sys, glob, os
from pathlib import Path

D = Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
REG = re.compile(r"ctx->(r\d+|hi|lo|f\d+)\b")
CALL = re.compile(r"\b([A-Za-z_][A-Za-z_0-9]*)\(rdram, ctx\)")
FUNC = re.compile(r"^(?:RECOMP_FUNC void|(?:static )?(?:int|void|uint32_t)) ([A-Za-z_][A-Za-z_0-9]*)\(uint8_t\* rdram, recomp_context\* ctx\) \{")
LABEL = re.compile(r"^\s*([A-Za-z_]\w*):\s*$")
GOTO = re.compile(r"goto ([A-Za-z_]\w*);")
# Patches whose hook writes guest registers ON PURPOSE (value substitution, reviewed s7477):
INTENT = {"s6904 fog": ({"f0", "f4"}, "rs64_s6904_fog rewrites the fog multiplier/offset that trunc.w.s at 0x8001726C/74 consume")}
ARGREGS = {"r4", "r5", "r6", "r7", "f12", "f13", "f14", "f15"}  # read by a guest call
CALLER_SAVED = {f"r{i}" for i in list(range(1, 16)) + [24, 25]} | {"hi", "lo"} | {f"f{i}" for i in range(0, 20)}

def load():
    bodies = {}
    for fn in sorted(glob.glob(str(D / "*.c"))):
        lines = Path(fn).read_text(errors="replace").split("\n")
        i = 0
        while i < len(lines):
            m = FUNC.match(lines[i])
            if m:
                j = i + 1
                while j < len(lines) and lines[j] != "}" and lines[j] != ";}" and not FUNC.match(lines[j]):
                    j += 1
                bodies[m.group(1)] = (os.path.basename(fn), i + 1, lines[i + 1:j])
                i = j - 1 if j < len(lines) and FUNC.match(lines[j]) else j
            i += 1
    # host helpers (src/**/*.cpp|c): brace-matched bodies of `name(uint8_t* rdram, recomp_context* ctx) {`
    HOST = re.compile(r"\b([A-Za-z_]\w*)\(uint8_t\s*\*\s*rdram,\s*recomp_context\s*\*\s*ctx\)\s*\{")
    srcroot = Path(__file__).resolve().parent.parent / "src"
    for fn in sorted(list(srcroot.rglob("*.cpp")) + list(srcroot.rglob("*.c"))):
        t = fn.read_text(errors="replace")
        for m in HOST.finditer(t):
            if m.group(1) in bodies:
                continue
            depth, j = 0, m.end() - 1
            while j < len(t):
                depth += t[j] == "{"; depth -= t[j] == "}"
                if depth == 0:
                    break
                j += 1
            bodies[m.group(1)] = (fn.name, t.count("\n", 0, m.start()) + 1, t[m.end():j].split("\n"))
    return bodies

def stmts(line):
    # strip // comments; split statements
    line = line.split("//")[0] if not line.lstrip().startswith("{ /*") else line
    return line.split(";")

def writes_of(text):
    w = set()
    for s in stmts(text):
        m = re.match(r"\s*(?:\{\s*)?ctx->(r\d+|hi|lo|f\d+)(?:\.\w+)?\s*=[^=]", s)
        if m:
            w.add(m.group(1))
        for m in re.finditer(r"ctx->(r\d+|hi|lo|f\d+)(?:\.\w+)?\s*=[^=]", s):
            w.add(m.group(1))
    return w

_clob = {}
def clob(name, bodies, stack=()):
    if name in _clob:
        return _clob[name]
    if name not in bodies or name in stack:
        return None if name not in bodies else set()
    w = set()
    for ln in bodies[name][2]:
        w |= writes_of(ln)
        for c in CALL.findall(ln):
            if c == name:
                continue
            cw = clob(c, bodies, stack + (name,))
            w |= cw if cw is not None else set(CALLER_SAVED)
    w = {r for r in w if r in CALLER_SAVED}   # o32: s0-s7, sp, fp, ra, f20-f31 are restored before return
    _clob[name] = w
    return w

_entry = {}
BODIES = {}
def entry_args(name):
    """argument regs a callee reads before writing (its arity as the generated code sees it)."""
    if name in _entry:
        return _entry[name]
    if name not in BODIES or not BODIES[name][0].startswith("funcs_"):
        return ARGREGS
    _entry[name] = ARGREGS                          # recursion guard: conservative
    lines = BODIES[name][2]
    labels = {LABEL.match(l).group(1): i for i, l in enumerate(lines) if LABEL.match(l)}
    _entry[name] = first_use(lines, -1, labels) & ARGREGS
    return _entry[name]

def first_use(lines, start, labels):
    """regs read-before-written after line index `start` (exclusive)."""
    live, seen_w = set(), {}
    work, visited = [(start + 1, frozenset())], set()
    for g in (GOTO.findall(lines[start]) if start >= 0 else []):          # a hook may jump out of the patch line itself (s6963_pre)
        if g in labels:
            work.append((labels[g], frozenset()))
    while work:
        i, killed = work.pop()
        while 0 <= i < len(lines):
            key = (i, killed)
            if key in visited:
                break
            visited.add(key)
            ln = lines[i]
            code = ln.split("//")[0]
            if "PATCH" in ln and code.strip().startswith("{ /*") is False and "/* PATCH" in code and not code.strip().startswith("{"):
                pass
            k = set(killed)
            calls = CALL.findall(code)
            for s in code.split(";"):
                m = re.match(r"\s*ctx->(r\d+|hi|lo|f\d+)(?:\.\w+)?\s*=[^=](.*)", s)
                rhs = m.group(2) if m else s
                for r in REG.findall(rhs):
                    if r not in k:
                        live.add(r)
                if m:
                    k.add(m.group(1))
            if calls and "PATCH" not in ln:
                # a guest call reads its argument regs; every caller-saved reg is dead after it
                for c in calls:
                    live |= entry_args(c) - k
                k |= CALLER_SAVED
            for g in GOTO.findall(code):
                if g in labels:
                    work.append((labels[g], frozenset(k)))
            if re.search(r"\breturn\b", code) or re.match(r"\s*goto \w+;", code):
                break
            killed = frozenset(k)
            i += 1
    return live

def unmarked_injection(lines, i):
    """a `f(rdram, ctx);` line with no PATCH tag that is not the translation of a jal/jalr/bal-class site."""
    ln = lines[i]
    if not CALL.search(ln) or "*ctx = sv" in ln:
        return False
    cm = [x for x in lines[max(0, i - 40):i] if re.match(r"\s*// 0x[0-9A-F]{8}:", x)][-2:]
    return not any(re.search(r":\s+(jal|jalr|j|jr|b\w*al)\s", x) for x in cm)

def audit(bodies, override=None):
    rows = []
    for caller, (fname, base, lines) in sorted(bodies.items()):
        if not fname.startswith("funcs_"):
            continue                                # host helpers are callees here, not audited callers
        if override and caller in override:
            lines = override[caller]
        labels = {}
        for i, ln in enumerate(lines):
            m = LABEL.match(ln)
            if m:
                labels[m.group(1)] = i
        for i, ln in enumerate(lines):
            if "PATCH" not in ln and not unmarked_injection(lines, i):
                continue
            calls = [c for c in CALL.findall(ln) if c != caller]
            if not calls:
                continue
            cl = set()
            unknown = []
            for c in calls:
                cw = clob(c, bodies)
                if cw is None:
                    unknown.append(c)
                else:
                    cl |= cw
            last = max(ln.rfind(c + "(rdram, ctx)") for c in calls)
            rest = writes_of(ln[last:])
            # a call followed by `return;` on its own line is a tail call: caller-saved regs are dead at return
            live = set() if re.search(r"\breturn\b", ln[last:]) else first_use(lines, i, labels)
            # REPLACE: the patch stands in for the site's own jal (next line `goto after_N;` skips the duplicate
            # delay slot). The o32 ABI already lets that call clobber every caller-saved reg, so only an injected
            # (extra) call can break live state.
            nxt = next((l for l in lines[i + 1:i + 3] if l.strip()), "")
            replace = bool(re.match(r"\s*goto after_\d+;", nxt))
            pname = (re.search(r"PATCH:?\s*([^*]{0,50})", ln) or [None, "?"])[1].strip()
            intent = INTENT.get(pname, (set(), ""))[0]
            bug = [] if replace else sorted((cl & live) - rest - intent)
            m = re.search(r"PATCH:?\s*([^*]{0,50})", ln)
            if "PATCH" not in ln:
                pname = "unmarked:" + pname
            rows.append(dict(caller=caller, file=fname, line=base + i + 1, patch=pname,
                             calls=calls, unknown=unknown, replace=replace, intent=sorted(cl & live & intent), clob=sorted(cl), rest=sorted(rest), bug=bug))
    return rows

def main():
    bodies = load()
    BODIES.update(bodies)
    rows = audit(bodies)
    # positive control: pre-s7476 s4889 text
    NEW = ("uint32_t saved_r4 = U32(ctx->r4), s7476_r5")
    ctl = "FAIL"
    if "reapplyAudioConfig" in bodies:
        f, b, lines = bodies["reapplyAudioConfig"]
        old = []
        for ln in lines:
            if "s4889 first gate-zero dereg" in ln:
                ln = re.sub(r"uint32_t saved_r4 = U32\(ctx->r4\), s7476_r5.*?s_done = 1; ",
                            "uint32_t saved_r4 = U32(ctx->r4); ctx->r4 = S32(0x8009123Cu); "
                            "findAndZeroTableSlotMatching(rdram, ctx); ctx->r4 = saved_r4; s_done = 1; ", ln)
            old.append(ln)
        crow = [r for r in audit({"reapplyAudioConfig": (f, b, old)}) if "s4889" in r["patch"]]
        nrow = [r for r in rows if r["caller"] == "reapplyAudioConfig" and "s4889" in r["patch"]]
        if crow and "r5" in crow[0]["bug"] and nrow and "r5" not in nrow[0]["bug"]:
            ctl = "PASS"
        print(f"[s7477] control old_s4889_bug={crow[0]['bug'] if crow else None} "
              f"new_s4889_bug={nrow[0]['bug'] if nrow else None} -> {ctl}")
    # synthetic control pair: an injected call before a read of $a1/$v1 must flag; the same call with restore must not
    pos = ["    ctx->r4 = ADD32(0, 1);", "    findAndZeroTableSlotMatching(rdram, ctx); /* PATCH: synth */",
           "    ctx->r2 = ADD32(ctx->r5, ctx->r3);", "    return;"]
    neg = list(pos); neg[1] = ("    { gpr a = ctx->r5, b = ctx->r3; findAndZeroTableSlotMatching(rdram, ctx); /* PATCH: synth */ "
                               "ctx->r5 = a; ctx->r3 = b; }")
    sp = audit({"synth": ("funcs_synth.c", 1, pos)})[0]["bug"]
    sn = audit({"synth": ("funcs_synth.c", 1, neg)})[0]["bug"]
    sctl = "PASS" if sp == ["r3", "r5"] and sn == [] else "FAIL"
    print(f"[s7477] synth_control pos_bug={sp} neg_bug={sn} -> {sctl}")
    if sctl != "PASS":
        ctl = "FAIL"
    nbug = 0
    for r in rows:
        tag = "BUG" if r["bug"] else ("REPLACE" if r["replace"] else ("INTENT" if r["intent"] else ("UNKNOWN" if r["unknown"] else "SAFE")))
        nbug += tag == "BUG"
        print(f"[s7477] {tag:7s} {r['file']}:{r['line']} caller={r['caller']} patch='{r['patch']}' calls={','.join(r['calls'])}"
              f" clob={','.join(r['clob']) or '-'} rest={','.join(r['rest']) or '-'} live_clobbered={','.join(r['bug']) or '-'}"
              + (f" unknown={','.join(r['unknown'])}" if r['unknown'] else ""))
    print(f"[s7477] summary sites={len(rows)} bug={nbug} control={ctl}")
    sys.exit(3 if ctl != "PASS" else (1 if nbug else 0))

if __name__ == "__main__":
    main()
