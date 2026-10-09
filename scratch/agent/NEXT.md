# Next work unit (s4348): static source census for the C904 family writer

HYPOTHESIS-ID: m5-step9-input-writer-source

Session 4347 selected the phase-gated input-span producer: retail writer
`0x8009DB2C` supplied exact `0x0010` values to C904 input spans. The generated
code shows this is a halfword store of `$t2` after clamping and `& 0xFFF8` in
the loop at `0x8009D980`; `0x8002A0B8/0x8002A0BC` are separate zero-writing
DMA/clear activity. The next unit is a bounded static census of the complete
writer idiom feeding `$t2` in `runVoiceLatticeFilter`, not another reactive
oracle run.

Competing hypotheses:

- H-lattice-legitimate: `0x8009DB2C` is the semantic producer; its `$t2`
  source is a legitimate lattice/filter result and the family value is an
  expected quantized sample/state value.
- H-lattice-input: `$t2` is derived from an earlier input field or table read;
  the census identifies a stable source address/field whose writer is the next
  boundary.
- H-aliased-buffer: the C904 span is reused storage and `0x8009DB2C` writes a
  later consumer buffer, so the apparent family match is a lifetime/alias
  coincidence; the function's pointer setup will show a non-C904 buffer role.

Discriminating measurement: enumerate every loop iteration's pointer setup and
all reads feeding `$t2` from the generated MIPS around `0x8009D980` through
`0x8009DB2C`, then join those reads to the C904 span geometry and companion
symbol names. A stable direct source field/table read selects H-lattice-input;
a clamped arithmetic-only result with the destination proven to be the active
voice output selects H-lattice-legitimate; a destination outside the active
C904 buffer role selects H-aliased-buffer. If static dataflow cannot split the
three, stop and design one batched retail witness before building.

Commands:

`rg -n -C 80 '0x8009D980|0x8009DB2C|0x8002A0B8|0x8002A0BC' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`

`rg -n -C 12 'runVoiceLatticeFilter|0x8009D980|0x8009DB2C' docs scratch /Users/williambuckley/Documents/Tools/rogue_squadron64`

Do not change decoder, RSP, AI, or runtime behavior. If the static census
cannot discriminate, do not build an instrument; write the blocker and a new
ground-truth measurement into NEXT.md instead.
