#!/usr/bin/env python3
"""s7591 class MR census: every call in OUR code that hands the caller a Mach right / kernel-allocated buffer it owns.

Scope: src/, lib/N64ModernRuntime (ultramodern, librecomp, thirdparty actually linked), lib/rt64/src incl. contrib/plume.
Excluded: vendored SDL, fmt/gtest test sources (not linked into the game).

Per site the tool finds the enclosing outermost non-namespace block (function, or class for ctor/dtor pairs) and looks
for the matching release inside it:
  task_threads(t,&A,&N)        -> needs vm_deallocate(..A..) AND mach_port_deallocate(..A[..]..)
  host_processor_info(..,&A,..)-> needs vm_deallocate(..A..)
  mach_thread_self/mach_host_self/thread_self -> one user ref per call: assigned var needs mach_port_deallocate(..var..);
                                  'static' init = bounded (one ref, ever); inline as an argument = leaked-uref per call
  semaphore_create(t,&S,..)    -> semaphore_destroy(..S..)
  IOServiceGetMatchingService / IORegistryEntryGetParentEntry / IOIteratorNext / IOServiceOpen -> IOObjectRelease/IOServiceClose
  mach_port_allocate/construct(..,&P) -> mach_port_mod_refs / mach_port_destruct / mach_port_deallocate (..P..)
  vm_allocate/mach_vm_allocate/mach_vm_read(..,&A,..) -> vm_deallocate/mach_vm_deallocate(..A..)
Borrowed (no ref taken, not rows): mach_task_self, pthread_mach_thread_np, pthread_from_mach_thread_np.
Verdict = released | bounded | leaked-uref | leaked-array | leaked-elem | leaked | unknown, gate = env-gated if the
function (or a GATES annotation) shows it only runs under a diagnostic env, else default.

--controls: classifies a planted scratch file (one site of each verdict) and exits nonzero if any is misclassified.
Exit nonzero on any unknown row or any leaked-* row whose gate is 'default'.
"""
import os, re, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ["src", "lib/N64ModernRuntime", "lib/rt64/src"]
SKIP = re.compile(r"(/N64Recomp/lib/|/test/|/tests/|gtest|gmock|/SDL)")
EXTS = (".c", ".cc", ".cpp", ".h", ".hpp", ".m", ".mm")
ACQ = re.compile(r"\b(task_threads|host_processor_info|mach_thread_self|mach_host_self|thread_self|semaphore_create|"
                 r"IOServiceGetMatchingService|IORegistryEntryGetParentEntry|IOIteratorNext|IOServiceOpen|"
                 r"mach_port_allocate|mach_port_construct|vm_allocate|mach_vm_allocate|mach_vm_read)\s*\(")
# Gate annotations for functions whose env check lives in a caller (file suffix, text inside the function, env, why).
GATES = [
    ("ultramodern/src/events.cpp", "g1e-thr-sampler", "ROGUESQ_G1E_THREADS", "g1et::run is started only by the G1E_THREADS lambda"),
    ("src/main/main.cpp", "[fl-zero-poll-gbt]", "fl-zero poll", "fl_zero_sample_game_threads runs only from the fl-zero poller"),
    ("src/main/main.cpp", "[s7382]", "ROGUESQ_S7382_QOS", "s7382_qos_dump runs only from s7382_qos_start's thread"),
    ("ultramodern/src/threads.cpp", "s7590_me", "ROGUESQ_G1B / s4587 sampler", "cached once, sampler is env-started"),
]

def strip(src):
    """blank comments and string/char literals, keep offsets"""
    out = list(src); i = 0; n = len(src)
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i); j = n if j < 0 else j
            for k in range(i, j): out[k] = " "
            i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2); j = n if j < 0 else j + 2
            for k in range(i, j):
                if out[k] != "\n": out[k] = " "
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            for k in range(i + 1, min(j, n)): out[k] = " "
            i = j + 1
        else:
            i += 1
    return "".join(out)

def enclosing(s, pos):
    """span of the outermost brace block containing pos that is not a namespace / extern "C" block"""
    stack = []
    for m in re.finditer(r"[{}]", s[:pos]):
        if m.group() == "{":
            head = s[max(0, m.start() - 160):m.start()]
            head = head[head.rfind(";") + 1:] if ";" in head else head
            kind = "ns" if re.search(r"\b(namespace\b[\w:\s]*|extern\s*$)\s*$", head.rstrip()) or re.search(r"namespace\s*[\w:]*\s*$", head) else "blk"
            stack.append((m.start(), kind))
        elif stack:
            stack.pop()
    start = next((p for p, k in stack if k != "ns"), None)
    if start is None: return 0, len(s)
    d = 0
    for m in re.finditer(r"[{}]", s[start:]):
        d += 1 if m.group() == "{" else -1
        if d == 0: return start, start + m.end()
    return start, len(s)

def args_of(s, i):
    """i at '(' -> list of top-level argument strings"""
    d = 0; cur = ""; out = []
    for c in s[i:]:
        if c == "(":
            d += 1
            if d == 1: continue
        elif c == ")":
            d -= 1
            if d == 0: out.append(cur.strip()); return out
        elif c == "," and d == 1:
            out.append(cur.strip()); cur = ""; continue
        cur += c
    return out

def var(a):
    a = a.strip()
    return re.sub(r"^\(?\s*\w+\s*\*?\s*\)\s*", "", a).lstrip("&").strip() if a else ""

def has(body, fn, v, elem=False):
    v = re.escape(v)
    pat = rf"\b{fn}\s*\([^;]*\b{v}\s*\[" if elem else rf"\b{fn}\s*\([^;]*\b{v}\b"
    return re.search(pat, body) is not None

def classify(path, raw):
    s = strip(raw); rows = []
    for m in ACQ.finditer(s):
        fn = m.group(1); p = m.end() - 1
        line = s.count("\n", 0, m.start()) + 1
        lo, hi = enclosing(s, m.start()); body = s[lo:hi]; rawbody = raw[lo:hi]
        a = args_of(s, p); stmt_lo = max(s.rfind(";", 0, m.start()), s.rfind("{", 0, m.start()), s.rfind("}", 0, m.start())) + 1
        stmt = s[stmt_lo:m.start()]
        if fn == "task_threads":
            A = var(a[1]) if len(a) > 1 else ""
            arr = has(body, "vm_deallocate", A) or has(body, "mach_vm_deallocate", A)
            el = has(body, "mach_port_deallocate", A, elem=True)
            v = "released" if arr and el else ("leaked-elem" if arr else "leaked-array")
        elif fn == "host_processor_info":
            A = var(a[3]) if len(a) > 3 else ""
            v = "released" if has(body, "vm_deallocate", A) else "leaked-array"
        elif fn in ("mach_thread_self", "mach_host_self", "thread_self"):
            am = re.search(r"(\w+)\s*=\s*(?:\(\s*\w+\s*\)\s*)?$", stmt)
            if re.search(r"\bstatic\b", stmt): v = "bounded"
            elif am: v = "released" if has(body, "mach_port_deallocate", am.group(1)) else "leaked-uref"
            else: v = "leaked-uref"   # inline argument: a fresh user ref per call, never released
        elif fn == "semaphore_create":
            S = var(a[1]) if len(a) > 1 else ""
            v = "released" if has(body, "semaphore_destroy", S) else "leaked"
        elif fn in ("IOServiceGetMatchingService", "IOIteratorNext"):
            am = re.search(r"(\w+)\s*=\s*$", stmt)
            v = "released" if am and has(body, "IOObjectRelease", am.group(1)) else ("unknown" if not am else "leaked")
        elif fn == "IORegistryEntryGetParentEntry":
            P = var(a[2]) if len(a) > 2 else ""
            v = "released" if has(body, "IOObjectRelease", P) else "leaked"
        elif fn == "IOServiceOpen":
            C = var(a[3]) if len(a) > 3 else ""
            v = "released" if has(body, "IOServiceClose", C) else "leaked"
        elif fn in ("mach_port_allocate", "mach_port_construct"):
            P = var(a[-1]) if a else ""
            v = "released" if any(has(body, f, P) for f in ("mach_port_mod_refs", "mach_port_destruct", "mach_port_deallocate", "mach_port_destroy")) else "leaked"
        else:  # vm_allocate / mach_vm_allocate / mach_vm_read
            A = var(a[1] if fn != "mach_vm_read" else (a[3] if len(a) > 3 else "")) if len(a) > 1 else ""
            v = "released" if has(body, "vm_deallocate", A) or has(body, "mach_vm_deallocate", A) else "leaked-array"
        gate = "env-gated" if "getenv" in body else "default"
        why = "getenv in scope" if gate == "env-gated" else ""
        for suf, needle, env, w in GATES:
            if path.endswith(suf) and needle in rawbody:
                gate, why = "env-gated", f"{env}: {w}"
        rows.append((path, line, fn, v, gate, why))
    return rows

def walk():
    for d in DIRS:
        for r, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(r, f)
                if f.endswith(EXTS) and not SKIP.search(p): yield p

CTRL = r'''
#include <mach/mach.h>
void ok_threads(void){ thread_act_array_t th; mach_msg_type_number_t n; task_threads(mach_task_self(),&th,&n);
  for(unsigned i=0;i<n;i++) mach_port_deallocate(mach_task_self(), th[i]); vm_deallocate(mach_task_self(),(vm_address_t)th,n*4); }
void bad_elem(void){ thread_act_array_t th; mach_msg_type_number_t n; task_threads(mach_task_self(),&th,&n);
  vm_deallocate(mach_task_self(),(vm_address_t)th,n*4); }
void bad_arr(void){ thread_act_array_t th; mach_msg_type_number_t n; task_threads(mach_task_self(),&th,&n);
  for(unsigned i=0;i<n;i++) mach_port_deallocate(mach_task_self(), th[i]); }
void bad_uref(void){ natural_t c; processor_info_array_t pi; mach_msg_type_number_t pc;
  if (host_processor_info(mach_host_self(),PROCESSOR_CPU_LOAD_INFO,&c,&pi,&pc)==0) vm_deallocate(mach_task_self(),(vm_address_t)pi,pc*4); }
void ok_self(void){ thread_t me = mach_thread_self(); /* mach_thread_self() in a comment must not count */ mach_port_deallocate(mach_task_self(), me); }
void cached(void){ static const mach_port_t h = mach_host_self(); (void)h; }
void bad_hpi(void){ static const mach_port_t h = mach_host_self(); natural_t c; processor_info_array_t pi; mach_msg_type_number_t pc;
  host_processor_info(h,PROCESSOR_CPU_LOAD_INFO,&c,&pi,&pc); }
struct Sem { semaphore_t s; Sem(){ semaphore_create(mach_task_self(),&s,0,0); } ~Sem(){ semaphore_destroy(mach_task_self(), s); } };
void bad_sem(void){ semaphore_t s; semaphore_create(mach_task_self(),&s,0,0); }
'''
CTRL_EXPECT = [("task_threads", "released"), ("task_threads", "leaked-elem"), ("task_threads", "leaked-array"),
               ("host_processor_info", "released"), ("mach_host_self", "leaked-uref"), ("mach_thread_self", "released"),
               ("mach_host_self", "bounded"), ("mach_host_self", "bounded"), ("host_processor_info", "leaked-array"),
               ("semaphore_create", "released"), ("semaphore_create", "leaked")]

def controls():
    d = tempfile.mkdtemp(prefix="s7591ctl"); p = os.path.join(d, "plant.c"); open(p, "w").write(CTRL)
    got = [(r[2], r[3]) for r in classify(p, CTRL)]
    ok = got == CTRL_EXPECT
    print(f"controls: {sum(g == e for g, e in zip(got, CTRL_EXPECT))}/{len(CTRL_EXPECT)} {'PASS' if ok else 'FAIL'}")
    if not ok:
        for g, e in zip(got, CTRL_EXPECT): print("  ", g, "expect", e)
        if len(got) != len(CTRL_EXPECT): print("   count", len(got), "expect", len(CTRL_EXPECT))
    return ok

def main():
    ok = controls() if "--controls" in sys.argv else True
    rows = []
    for p in sorted(walk()):
        try: raw = open(p, encoding="utf-8", errors="replace").read()
        except OSError: continue
        if ACQ.search(raw): rows += classify(os.path.relpath(p, ROOT), raw)
    bad = 0
    for path, line, fn, v, gate, why in rows:
        flag = "" if v in ("released", "bounded") else (" <-- OPEN" if gate == "default" or v == "unknown" else " (gated)")
        bad += flag == " <-- OPEN"
        print(f"{path}:{line} {fn} {v} {gate}{(' [' + why + ']') if why else ''}{flag}")
    from collections import Counter
    c = Counter(r[3] for r in rows)
    print(f"rows={len(rows)} " + " ".join(f"{k}={c[k]}" for k in sorted(c)) +
          f" gated_leaks={sum(1 for r in rows if r[3].startswith('leaked') and r[4] == 'env-gated')} open={bad}")
    sys.exit(0 if ok and bad == 0 else 1)

if __name__ == "__main__":
    main()
