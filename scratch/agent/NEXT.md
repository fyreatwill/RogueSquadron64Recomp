# NEXT (s7349): idiom-class audit - class Z, shift by a guest-derived count with no range check
HYPOTHESIS-ID: host-shift-count
Context: s7348 closed class Y (tools/s7348_div_census.py: 1512 / % ops, 214 sites, 0 open; RT64 4b pixelSize and librecomp
guest 64-bit div helpers fixed).
Sibling idiom: `x << n` / `x >> n` where n comes from guest data (RDP tile shifts/masks fields, siz in `1 << siz`, ucode / task
fields, VI registers, MEM_* reads) with no `n < 32` / `& 31` / min() check. n >= operand width or negative is UB in C++ (arm64 and
x86 mask the count, but clang may fold assuming n < width); `1 << 31` on a signed int is UB before C++20.
Hypotheses: H-safe (every count is a literal, masked by a <= 5-bit field (`& 0xF` / `& 0x1F`), or range-checked), H-diag (only
gated probes), H-ub (a default-on guest count can reach >= width: real defect, fix with a mask/clamp matching hardware).
Method: new tools/s7349_shift_census.py on the s7343 scope; reuse s7348 rhs_of()/lhs_of()/strip_div() (operand parsing), s7342 ev()
for constants, s7344 decl() and s7344 MSK logic (narrow types, `& 0x..` masks give a max count). Sites: `<<` / `>>` (not stream
`<<`, not templates `>>`, not `<<=` in comments) whose count is not a literal/constexpr. Classes: K, MSK (count masked or narrow
type with max < operand width), RC (range-checked before), BC, G/D/P/C, H hand, B default-on guest count unchecked. Note the
operand width (32 vs 64) when judging MSK. Controls: planted `uint32_t n = tile->shifts; return x << n;` ('?'), masked twin
(`& 0xF` -> MSK), checked twin (RC), gated twin (G), stream twin (`std::cout << n`, not a site).
Runtime only if a B site exists: fix + standalone control, then `env SECS=260 zsh scratch/s7326/run.zsh s7349_dd8 ''`.
Exit: PORTING-STATE s7349, CURRENT-TRUTH item 27n -> closed/fixed, commit.
