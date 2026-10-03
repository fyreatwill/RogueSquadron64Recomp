# Next work unit: audit the complete `rs_zcfree` incoming `$a0` idiom

HYPOTHESIS-ID: m3-zcfree-a0-idiom-audit

The M5 route comparison is parked: s3789 had a valid retail control and a
valid image arm, but the silent arm crashed before paired family rows. Do not
repeat that recipe without a new arm-stability discriminator.

Competing hypotheses and discriminator:

- H1: every `rs_zcfree` call at `0x80005268` receives a legitimate heap
  pointer from a known allocator/object lifetime; no guard is justified.
- H2: one or more incoming writers produce a concrete invalid value; the
  complete idiom census identifies the writer and a narrowly scoped guard is
  justified only if the writer is proven non-legitimate.
- H3: the apparent invalid input is a register/ABI interpretation artifact or
  a dead path; callsites and value provenance cannot establish a real invalid
  writer, so land no mitigation and document the boundary.

The discriminating measurement is one complete source census of all calls and
all incoming `$a0` setup idioms for `rs_zcfree` at `0x80005268`, joined to the
existing generated symbols and allocator/object lifetime evidence. H1/H2/H3
are decided only after every callsite in the idiom class is classified; a
single crash or a single suspicious value is insufficient.

Exact commands:

    rg -n "80005268|rs_zcfree|zcfree" RecompiledFuncs docs src lib
    rg -n "func_80005268|0x80005268" RecompiledFuncs docs PORTING-STATE.md | tail -40

Before any build, enumerate the complete callsite table in a new bounded note
under `docs/`, including caller, `$a0` writer, object/lifetime proof, and
legitimacy. If H2 is proven, implement one guarded override through the
patches pipeline and build/validate it; otherwise land the census note with
no mitigation.
