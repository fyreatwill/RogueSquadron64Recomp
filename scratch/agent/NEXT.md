# NEXT (s7358): idiom-class audit - class AI, unvalidated numeric env/config parses
HYPOTHESIS-ID: host-unvalidated-numeric-parse
Context: s7357 closed class AH (unchecked I/O lengths; census tools/s7357_iolen_census.py, arms tools/s7357_arms.zsh).
Idiom (class AI): in host C++ we own (src/, lib/N64ModernRuntime/{librecomp,ultramodern}/src, our lib/rt64 '+' lines),
atoi/atol/strtol/strtoul/strtoull/atof/strtod/sscanf on a getenv value or config-file text, whose result is then used as an
array index, allocation size/count, shift amount, divisor or loop bound with no clamp. A typo'd or negative ROGUESQ_* value
(owner opt-ins: ROGUESQ_DRAW_DISTANCE, ROGUESQ_ASPECT, ROGUESQ_RESMULT, ROGUESQ_UCODE_CAP, FOG_ALT, ...) then indexes out of
bounds, divides by zero or allocates huge.
Hypotheses: H-safe (every default-on owner knob is clamped), H-diag (only diagnostic knobs are unclamped: harmless-ish),
H-unclamped (an owner-facing opt-in, or any default-on parse, reaches an index/size/shift/divisor unclamped: fix with a clamp
+ named warning).
Method: tools/s7358_envparse_census.py: enumerate parse calls; follow the result variable forward (same function / static
init lambda) to its first sink use; classify CLAMPED (min/max/std::clamp/if range test before the sink) / NOSINK (only
printed / compared) / G (diagnostic knob) / B (owner knob or default-on, unclamped sink) / ?. MANUAL table like s7356/s7357.
Controls: planted unclamped index (B), clamped twin, printed-only twin. Second line: for each B, run the game with the bad
value (e.g. ROGUESQ_X=-1 / 0 / 99999999) pre-fix vs post-fix, 20 s boot arms like tools/s7357_arms.zsh (own working folder
with a save COPY; never touch build/saves). Then 260 s dd8 smoke: `env SECS=260 zsh scratch/s7326/run.zsh s7358_dd8 ''`.
Exit: PORTING-STATE s7358, CURRENT-TRUTH item 27w -> closed, commit.
