# Next work unit

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Begin the generated-symbol sweep only after the required revisit preflight.
Run `grep -n '^## Session ' PORTING-STATE.md | tail -15`. If all 15 titles
contain `synchronized`, `confirmed ... symbol`, or a sweep-scoped census that
selected H2/H3, this is a REVISIT instead: use a genuinely new angle on the
CURRENT-TRUTH external retail-entry boundary, with its existing independent
whole-RDRAM/title/hangar controls, or the M4 accumulator boundary. Do not add
another sweep diagnostic field.

Otherwise, audit the next ranked generated placeholder from the current
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs` tree against
the companion symbol/m2c sources. Rename exactly one function only if all three
gates pass: a semantic companion mapping exists, the function has a live caller
or independently meaningful body, and the mapped span agrees exactly. If any
gate fails, record the candidate as retained and move to the next ranked
candidate in the same bounded census; do not invent an address-based name.

Exact preflight/census commands:

    grep -n '^## Session ' PORTING-STATE.md | tail -15
    rg -n '^RECOMP_FUNC .*func_0x|^RECOMP_FUNC .*func_[0-9A-Fa-f]{8}' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
    rg -n '8000040C|800E9AE0|func_8000040C|func_800E9AE0' /Users/williambuckley/Documents/Tools/rogue_squadron64 2>/dev/null

Expected discriminator: either one candidate satisfies all three rename gates,
selecting a bounded mapping change, or the census finds no eligible candidate
and the sweep remains parked while the revisit branch is selected. Do not build
or run the game unless a runtime discriminator is required by the revisit.
