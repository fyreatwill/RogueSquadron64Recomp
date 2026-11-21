#!/usr/bin/env python3
"""s7762: owner-doc staleness check.

For each owner-facing doc given (default docs/OWNER-REVIEW-QUEUE.md docs/OWNER-OPT-INS.md):
  PATH  every repo path it names (docs/..., scratch/..., tools/..., build/..., src/...) must exist;
  NAME  every ROGUESQ_* name it names must be READ by code that runs: a quoted literal "ROGUESQ_X" (or a reader helper
        call on the bare suffix, e.g. env_flag("X") with a ROGUESQ_ prefixing helper) in src/, include/, lib/rt64/src,
        lib/N64ModernRuntime, ../N64Recomp/RecompiledFuncs, build/factor5_ucode, RecompiledPatches, patches.
A name found only in docs/scripts is STALE (renamed or removed): the owner would type a setting that does nothing.
--controls: a planted fake name and a planted fake path must be flagged, and ROGUESQ_FPS60 / docs/OWNER-OPT-INS.md must
pass, in the same run. rc 0 = controls PASS and no STALE in the queue doc; 1 = stale; 3 = control failure.
Stale names in OWNER-OPT-INS are reported (rc 1 too) unless listed in OPT_OK with a reason."""
import glob, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREES = ["src", "include", "lib/rt64/src", "lib/N64ModernRuntime", "../N64Recomp/RecompiledFuncs", "build/factor5_ucode",
         "RecompiledPatches", "patches"]
NAME = re.compile(r"ROGUESQ_[A-Z0-9_]*[A-Z0-9]")
PATH = re.compile(r"(?<![\w/.])((?:docs|scratch|tools|build|src)/[A-Za-z0-9_./-]*[A-Za-z0-9_])")
# names documented as non-env things (cmake options) or read through a composed key; reason required
OPT_OK = {"ROGUESQ_SRC_OPT": "cmake option, not an env var", "ROGUESQ_FUNCS_OPT": "cmake option, not an env var",
          "ROGUESQ_NAME": "placeholder in the settings.txt line format (ROGUESQ_NAME=value)"}
# files the OWNER creates (absent until they do); reason required
PATH_OK = {"build/settings.txt": "owner-created launch settings file (rs64_settings.cpp reads it beside the exe)",
           "build/controls.json": "owner-created custom controls file (missing = default map)"}


def code_names():
    pat = re.compile(r'"(ROGUESQ_[A-Z0-9_]+)"')
    bare = re.compile(r'(?:env_flag|env_on|env_int|env_float|env_str|rs64_env\w*)\s*\(\s*"([A-Z0-9_]+)"')
    seen = set()
    exts = (".c", ".cc", ".cpp", ".h", ".hpp", ".mm", ".m", ".inl")
    for t in TREES:
        top = os.path.join(ROOT, t)
        for dp, _, fs in os.walk(top):
            for f in fs:
                if not f.endswith(exts):
                    continue
                try:
                    s = open(os.path.join(dp, f), errors="replace").read()
                except OSError:
                    continue
                if "ROGUESQ_" not in s and "env_" not in s:
                    continue
                seen.update(pat.findall(s))
                seen.update("ROGUESQ_" + b for b in bare.findall(s) if not b.startswith("ROGUESQ_"))
    return seen


def prefixes(seen):
    # "ROGUESQ_FOO_" + suffix composed readers: a literal ending in '_' covers FOO_*
    return {n for n in seen if n.endswith("_")}


def check(doc, text, seen, pre):
    bad_paths, bad_names, names = [], [], set(NAME.findall(text))
    for p in sorted(set(PATH.findall(text))):
        p = p.rstrip(".")
        if "*" in p or "<" in p or p in PATH_OK:
            continue
        if not os.path.exists(os.path.join(ROOT, p)):
            bad_paths.append(p)
    for n in sorted(names):
        if n in seen or n in OPT_OK or any(n.startswith(x) for x in pre):
            continue
        bad_names.append(n)
    return names, bad_paths, bad_names


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    docs = args or ["docs/OWNER-REVIEW-QUEUE.md", "docs/OWNER-OPT-INS.md"]
    seen = code_names()
    pre = prefixes(seen)
    rc = 0
    if "--controls" in sys.argv:
        plant = "set `ROGUESQ_S7762_NOSUCH_PLANT=1`, sheet docs/owner_sheet_s7762_nosuch.jpg; `ROGUESQ_FPS60=1` docs/OWNER-OPT-INS.md"
        _, bp, bn = check("plant", plant, seen, pre)
        ok = (bp == ["docs/owner_sheet_s7762_nosuch.jpg"] and bn == ["ROGUESQ_S7762_NOSUCH_PLANT"])
        print("CONTROL", "PASS" if ok else "FAIL", "paths=%s names=%s code_names=%d" % (bp, bn, len(seen)))
        if not ok:
            return 3
    for d in docs:
        text = open(os.path.join(ROOT, d), errors="replace").read()
        names, bp, bn = check(d, text, seen, pre)
        print("%s names=%d paths_missing=%d names_stale=%d" % (d, len(names), len(bp), len(bn)))
        for p in bp:
            print("  MISSING-PATH", p)
        for n in bn:
            print("  STALE-NAME", n)
        if bp or bn:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
