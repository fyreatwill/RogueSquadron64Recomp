# NEXT: identify the writer/translation that corrupts the 0x800903F0 input
HYPOTHESIS-ID: m5-audio-destub

s4595 completed the caller census. The retail oracle passed its whole-RDRAM
control and VI-512 target watch; its named builder PCs wrote B0xxxxxx
pointers. The port run reached VI-640/origin 0x006A2900 and passed four
adjacent-range controls. The first bad caller row was site 0x800903F0:
voice 0x801724C0 had raw +0x34=0x6C617465 ("late"), a1=0x6C63745D, and
a3=0x6C617465; FE98 received the same malformed a1/a3. The run ended at the
known odd-PI abort after the discriminator fired.

Next work unit: perform one bounded static census of every store to the
selected voice +0x34 and every instruction that builds a1/a3 on the
0x800903F0 path. Use the preserved generated source and companion decomp
symbols; do not build or run until the census names the candidate PCs and
their data-flow roles. Competing outcomes: (H-writer) a named guest store
puts printable data into voice +0x34 before the call; (H-builder) +0x34 is
legitimate but a caller arithmetic/load constructs printable a1/a3; (H-port)
neither source is printable statically, so the discrepancy is in a runtime
input/translation boundary. Discriminator: the complete store/use table for
the selected voice field and call-site operands, with no unclassified store
or builder remaining.

Commands:

    rg -n "0x34\)|0x34\(" ../N64Recomp/RecompiledFuncs/funcs_24.c
    rg -n "800903F0|800903E4|800903E8|800903EC|8008FAAC|8008FDC0" ../N64Recomp/RecompiledFuncs/funcs_24.c
    rg -n "801724C0|voice.*34|0x34" ../rogue_squadron64 src docs

Do not add a mitigation. If the static table is complete but cannot classify
the runtime writer, record that as the selected boundary and design the next
ground-truth watch before building another instrument.
