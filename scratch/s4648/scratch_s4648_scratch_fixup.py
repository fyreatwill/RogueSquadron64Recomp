"""Run fixup_game_funcs.py against a COPY of pristine regen output, never the live RecompiledFuncs.
Usage: python3 scratch_s4648_scratch_fixup.py   (creates ./scratch_s4648/RecompiledFuncs, runs patched copy of fixup)"""
import pathlib, shutil, subprocess, sys
root = pathlib.Path(__file__).resolve().parent
work = root / "scratch_s4648"
if work.exists():
    shutil.rmtree(work)
work.mkdir()
shutil.copytree(root / "RecompiledFuncs.s4204-fresh", work / "RecompiledFuncs")
src = (root / "fixup_game_funcs.py").read_text().splitlines(keepends=True)
assert src[26].startswith("base = pathlib.Path(")
src[26] = f'base = pathlib.Path("{work / "RecompiledFuncs"}")\n'
(work / "fixup_scratch.py").write_text("".join(src))
r = subprocess.run([sys.executable, str(work / "fixup_scratch.py")], capture_output=True, text=True, cwd=work)
out = (r.stdout + r.stderr)
(work / "out.log").write_text(out)
lines = out.splitlines()
print("rc", r.returncode, "lines", len(lines))
print("\n".join(l[:300] for l in lines[-8:]))
