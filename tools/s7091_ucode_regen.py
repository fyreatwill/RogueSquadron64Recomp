#!/usr/bin/env python3
"""s7091: rebuild the fixed RSP ucode C files from a FRESH RSPRecomp pass, and census the fixup layer.

Why: build/factor5_ucode/*.c is gitignored, and tools/fixup_factor5_ucode.py is NOT a fresh-regen
script: its 70+ blocks were added one at a time and run on the already-fixed file, so several blocks
anchor on text that a block LATER in the file inserts (s7091: 6d anchors on fixup 9's
rs64_e9prov_l1db0_predecessor line; fixup 24 was not gated to the main ucode and exits 1 on the audio
and boot files before anything is written). A fresh pass through the plain script therefore fails.

RESULT s7091: even transactional multipass does NOT reproduce the live files. Fresh, these blocks never
apply: main 13, 14, 15, 16, 17, 13b, 19, 19b(+22 probes), 21, 22, 20, 21(store attest); ovl20 19, 19b; and
the "#include <cstdio>" line (inside the un-gated fixup 24 block) on audio/boot/ovl20. Their anchors name
text that later blocks rewrote (e.g. fixup 13 anchors "> 16384", since changed to rs64_cap_v; fixup 19's
v1->v2 migration branch fires on fresh text and exits before its fresh-install branch). The supported
fresh-regen path is therefore tools/ucode_regen.sh (RSPRecomp + tools/ucode_fixed/*.patch), whose patch
content tools/s7091_ucode_insn_census.py audits. This driver stays as the diagnostic for that list.

This driver splits the script into its "# Fixup" blocks and runs them TRANSACTIONALLY (a block that
exits on a failed anchor is rolled back) in repeated passes until a pass changes nothing, i.e. it
reproduces the historical accumulation order. Files run in dependency order: ovl20 first (main's
splice of overlay 0x20 copies the fixed ovl20 text), then main, audio, boot.

Census (per file): every line of the result that is not a pristine RSPRecomp line is attributed to
the block that inserted it; every pristine RSP instruction comment ("// mnem  ops") is counted in the
pristine file and in the result. A retail-instruction count that differs without being explained by a
splice (main ucode: + the instruction comments of the spliced overlay text) is a defect.

Usage:
  s7091_ucode_regen.py regen <pristine_dir> <out_dir>      # run RSPRecomp output through the blocks
  s7091_ucode_regen.py compare <out_dir> <live_dir>        # byte compare vs build/factor5_ucode
  s7091_ucode_regen.py census <pristine_dir> <out_dir>     # per-block attribution + instruction census
Exit 1 on any mismatch / unattributed defect.
"""
import collections, io, re, shutil, sys, contextlib
from pathlib import Path

SCRIPT = Path(__file__).with_name("fixup_factor5_ucode.py")
ORDER = ["factor5_ucode_ovl20_recompiled.c", "factor5_ucode_recompiled.c",
         "factor5_ucode_b_recompiled.c", "factor5_boot_recompiled.c"]
INSN = re.compile(r"^\s*// ([a-z][a-z0-9.]*)(?: {2,}\S.*)?$")


def blocks():
    lines = SCRIPT.read_text().split("\n")
    heads = [i - 1 for i, l in enumerate(lines) if l.startswith("# Fixup") and i > 0 and lines[i - 1].startswith("# ---")]
    end = next(i for i, l in enumerate(lines) if l.startswith("if text == original:"))
    pre = "\n".join(lines[:heads[0]])
    chunks = []
    for a, b in zip(heads, heads[1:] + [end]):
        name = lines[a + 1][2:].split(":")[0].strip()
        chunks.append((f"{name}@{a + 2}", "\n".join(lines[a:b])))
    epi = "\n".join(lines[end:])
    return pre, chunks, epi


def run_file(path, trace=None):
    pre, chunks, epi = blocks()
    g = {"__name__": "__main__", "__file__": str(SCRIPT)}
    old_argv = sys.argv
    sys.argv = [str(SCRIPT), str(path)]
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            exec(compile(pre, str(SCRIPT), "exec"), g)
            applied, passes = [], 0
            while True:
                passes += 1
                changed = False
                for name, src in chunks:
                    snap = g["text"]
                    try:
                        exec(compile(src, f"{SCRIPT}:{name}", "exec"), g)
                    except SystemExit:
                        g["text"] = snap
                        continue
                    if g["text"] != snap:
                        changed = True
                        applied.append((passes, name))
                        if trace is not None:
                            trace.append((name, snap, g["text"]))
                if not changed or passes >= 25:
                    break
            # epilogue: write + the s4210/s4220 audio tail. patch_rsp() edits lib/ — stub it (lib/ already
            # carries it; this driver must never write under lib/).
            import importlib.util as ilu
            real = ilu.spec_from_file_location
            def spec(name, loc, *a, **k):
                s = real(name, loc, *a, **k)
                if name == "apply_s4220_snap":
                    orig = s.loader.exec_module
                    def em(m):
                        orig(m); m.patch_rsp = lambda: None
                    s.loader.exec_module = em
                return s
            ilu.spec_from_file_location = spec
            try:
                exec(compile(epi, f"{SCRIPT}:epilogue", "exec"), g)
            except SystemExit:
                pass
            except AssertionError:
                # the s4220 tail patches the AUDIO file from every run; before the audio file's own blocks
                # have run its anchor is absent. Non-fatal: the audio file's own run applies it.
                pass
            finally:
                ilu.spec_from_file_location = real
    finally:
        sys.argv = old_argv
    return applied, passes


def regen(pristine, out):
    out.mkdir(parents=True, exist_ok=True)
    for f in pristine.glob("*.c"):
        shutil.copy(f, out / f.name)
    traces = {}
    for name in ORDER:
        tr = []
        applied, passes = run_file(out / name, tr)
        traces[name] = tr
        print(f"{name}: {len(applied)} block applications over {passes} passes: "
              + ", ".join(f"p{p}:{n.split('@')[0]}" for p, n in applied))
    return traces


def compare(out, live):
    bad = 0
    for f in sorted(live.glob("*.c")):
        o = out / f.name
        same = o.exists() and o.read_bytes() == f.read_bytes()
        if not same:
            bad += 1
            import difflib
            d = list(difflib.unified_diff(f.read_text().split("\n"), o.read_text().split("\n") if o.exists() else [],
                                          "live/" + f.name, "regen/" + f.name, n=0, lineterm=""))
            print(f"DIFF {f.name}: {sum(1 for l in d if l[:1] in '+-' and l[:3] not in ('+++', '---'))} lines")
            for l in d[:30]:
                print("   ", l[:160])
        else:
            print(f"SAME {f.name}")
    return bad


def insn_counts(text):
    return collections.Counter(m.group(0).strip() for m in (INSN.match(l) for l in text.split("\n")) if m)


def census(pristine, out):
    """Per block: which retail-instruction comments it added / removed. Added ones must come from a splice
    source (pristine overlay file text); removed ones are defects unless the block says why."""
    ovl_src = collections.Counter()
    for f in pristine.glob("factor5_ucode_ovl*_recompiled.c"):
        ovl_src += insn_counts(f.read_text())
    work = out.parent / (out.name + "_census")
    if work.exists():
        shutil.rmtree(work)
    traces = regen(pristine, work)
    defects = 0
    rows = []
    for name in ORDER:
        for blk, before, after in traces[name]:
            a, b = insn_counts(before), insn_counts(after)
            add, rem = b - a, a - b
            n_add, n_rem = sum(add.values()), sum(rem.values())
            if not n_add and not n_rem:
                continue
            not_from_ovl = add - ovl_src
            rows.append((name, blk, n_add, n_rem, sum(not_from_ovl.values()), rem))
    print("\nfile | block | +retail insn | -retail insn | +not in any overlay source")
    for name, blk, n_add, n_rem, nf, rem in rows:
        print(f"{name} | {blk} | {n_add} | {n_rem} | {nf}" + (f" | removed: {dict(list(rem.items())[:6])}" if n_rem else ""))
    # whole-file: result vs pristine
    print("\nwhole file: pristine insn comments -> result")
    for name in ORDER:
        p = insn_counts((pristine / name).read_text())
        r = insn_counts((work / name).read_text())
        lost = p - r
        print(f"{name}: pristine {sum(p.values())} result {sum(r.values())} lost {sum(lost.values())}"
              + (f" {dict(lost)}" if lost else ""))
        defects += sum(lost.values())
    return defects, rows


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "regen":
        regen(Path(sys.argv[2]), Path(sys.argv[3]))
    elif cmd == "compare":
        sys.exit(1 if compare(Path(sys.argv[2]), Path(sys.argv[3])) else 0)
    elif cmd == "census":
        d, _ = census(Path(sys.argv[2]), Path(sys.argv[3]))
        sys.exit(1 if d else 0)
