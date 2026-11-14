# NEXT (s7353): idiom-class audit - class AD, invalid bool / enum values from guest-derived bytes
HYPOTHESIS-ID: host-bool-enum-load
Context: s7352 closed class AC (tools/s7352_signed_census.py: 407 sites + 178 blind-spot rows, 0 open, no defect).
Idiom: a host `bool` (or a struct with a bool member) filled from RDRAM / DL / OSTask bytes by memcpy, a cast pointer or
`*(bool*)`. Also `static_cast<Enum>(guest)` / `(Enum)w0 field`, where the field can exceed the enum's range (enum class without a
fixed underlying type, or a plain enum whose value range is narrower than the field). Also a `switch` / table index on such an enum.
Loading a bool not 0/1 or an out-of-range enum is UB: clang may drop default: branches or treat the bool as 0..255.
Hypotheses: H-safe (every bool is computed by a comparison / `!= 0`; every enum cast has a fixed underlying type that covers the
field width, e.g. `enum class X : uint8_t` from an 8-bit field), H-diag (only gated probes), H-ub (default-on bool/enum load from
an unconstrained guest byte/field: fix with `!= 0` or a range check before the cast).
Method: new tools/s7353_boolenum_census.py on the s7343 scope; reuse s7338 sites() C/P/G/D, s7343 ln_fn/body_gated/hand, s7344
decl/CORE, s7346 hdr_text/member_types. Sites:
  (a) `static_cast<E>(` / `(E)` where E is an enum type (collect enum names and their underlying types from the scope headers);
  (b) memcpy / cast-pointer reads into a bool or a struct containing bool (s7350/s7351 site lists give the guest copies);
  (c) `bool x = <guest int>` without a comparison (implicit int -> bool conversion is FINE: count it as SAFE, it is not a load).
Classes: FIXED (underlying type covers the field width), CMP (value produced by a comparison), RC (range-checked before the cast),
H, B. Controls: planted `Mode m = static_cast<Mode>(task->a);` with an unfixed `enum class Mode { A, B }` ('?'), a fixed `: uint32_t`
twin (FIXED), a range-checked twin (RC), a gated twin (G), and a `bool b = task->a;` twin (SAFE, not a site).
Runtime only if a B site gets fixed: standalone UBSan control (-fsanitize=bool,enum), then
`env SECS=260 zsh scratch/s7326/run.zsh s7353_dd8 ''`.
Exit: PORTING-STATE s7353, CURRENT-TRUTH item 27r -> closed/fixed, commit.
