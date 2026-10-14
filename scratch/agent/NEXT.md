# Resume next work unit

HYPOTHESIS-ID: m3-hi16-lo16-pairs

WORK UNIT: perform one complete census of generated HI16/LO16 address-pair
idioms. Do not chase a single wild address and do not add a guard before the
whole class is enumerated.

Competing hypotheses:

* H-hi-lo-faithful: every generated HI16/LO16 pair preserves the MIPS
  relocation/rounding contract and uses the intended paired low half.
* H-hi-lo-mismatch: at least one generated pair combines the wrong HI16 and
  LO16 or loses the carry-adjusted high half, producing a wrong address.
* H-hi-lo-intervening-write: at least one pair is separated by a register
  overwrite or memory operation that changes the value before the low-half
  merge, making the construction unsafe.
* H-hi-lo-route-gap: all suspicious candidates are outside the qualified
  title/hangar route, so static evidence cannot select a runtime defect.

DISCRIMINATING MEASUREMENT: enumerate every `lui`/high-half and low-half
address construction in generated `funcs_*.c`, map each to its guest PC and
function, and classify the intervening instruction sequence, destination
register, low-half merge, and derived address use. H-hi-lo-faithful is selected
if every pair has the expected preserved register and merge semantics;
H-hi-lo-mismatch if a pair demonstrably uses a wrong high/low relationship;
H-hi-lo-intervening-write if a pair is clobbered before its merge; and
H-hi-lo-route-gap if the remaining suspicious candidates lack route evidence.
The qualified title/hangar phase/SP/PCM route is the positive control, but no
site-level reachability claim may be made from it alone.

Exact commands:

    rg -n -i -C 4 'lui|addiu|ori|lui.*0x801|0x[0-9A-Fa-f]+.*(lui|addiu|ori)' ../N64Recomp/RecompiledFuncs/funcs_*.c
    rg -n -i -C 4 'HI16|LO16|hi16|lo16|high half|low half|reloc' tools docs ../N64Recomp 2>/dev/null
    grep -n '^## Session ' PORTING-STATE.md | tail -15

Write the bounded census to a new `docs/M3-S4838-HILO-CENSUS.md` only if the
class is found and classified. If a real runtime defect is proven, land the
smallest durable fix through the appropriate fixup script; otherwise the
census itself is the work result. Do not build or run until the hypotheses and
the discriminator above are still sufficient for every possible outcome.
