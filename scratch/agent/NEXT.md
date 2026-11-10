# NEXT: owner reports first; otherwise N64Recomp silent-lowering census (jr $reg + jump tables)
HYPOTHESIS-ID: n64recomp-silent-lowering-census
Context: s7082 closed every class N64Recomp WARNS about (docs/N64RECOMP-WARNING-CENSUS.md). Lowerings it does not warn
about: 81 `LOOKUP_FUNC(ctx->rN)` sites (jr $non-ra treated as tail call) and 177 `switch (jr_addend...)` jump tables in
scratch/s7082/regen (pristine front-end output, regenerate with tools/regen_front.sh if cleaned).
Unit (offline, one bounded change):
1. Enumerate both. For each jr-$reg site: is it a real tail call / function-pointer jump (H-tail), a jump table N64Recomp
   failed to recognise (H-missed-table: the register comes from a lw off a lui/addiu table base + index), or decoded data?
2. For each jump table: read the table from the ROM (tools/s7082_jal_census.py shows how to map vram->rom per section) and
   check every entry lands on a printed label inside the same function and the case count matches the bound check (sltiu).
3. Any H-missed-table or bad-entry row: generic fixup + differential test with tools/s7081_selfbranch_test/mips_ref.py.
Discriminator: site x {tail, missed-table, data} and table x {all entries in-function, some out}. Closes when every site
has a class. Positive control: a known table (e.g. one in mainGameLoop) must classify all-in.
