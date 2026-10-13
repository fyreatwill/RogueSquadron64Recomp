# UNBLOCK s4742 (2026-10-13)

Route taken: 3 (re-scope), after routes 1 and 2 were checked and failed.

Route 1 (refute): the only dependency is running `../N64Recomp/build/RSPRecomp`.
Searched tools/, Makefile, CMakeLists.txt, scratch/agent/*.sh for an existing
allowlisted wrapper: none runs RSPRecomp (matches are comments / docstrings).
The binary exists. .claude/settings.json has no RSPRecomp allow rule, so the
denial is real, not a mis-reading.
Route 2 (satisfy locally): the only ways are editing the permission allowlist,
or wrapping the call in `zsh -c` / a new tools/ script that the `Bash(zsh:*)` and
`Bash(tools/*)` rules would pass. The first is a permission-setting change and
the second sidesteps a denial on that specific binary. Both are on the hard
boundary list, so not done.
Route 3: NEXT.md rewritten to an offline unit (static analysis of the 0x2C image
and a drafted-but-unwired fixup 6r). Open dependency recorded in CURRENT-TRUTH.

To clear the dependency, a human adds to .claude/settings.json allow:
  "Bash(../N64Recomp/build/RSPRecomp:*)" and
  "Bash(/Users/williambuckley/Documents/Tools/N64Recomp/build/RSPRecomp:*)"
Experiment that would refute "this needs a human": any allowlisted tool that
emits the RSPRecomp C for factor5_rsp_ovl2c.toml (none found).
