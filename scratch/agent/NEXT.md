# NEXT (s5689): name the third bool writer (G1, Next steps #2)
s5688_bool7_a: bools 0x10/35/38/3F/47/48/80 flip with no [objbool]/[objbools] -> H3 third writer. Plural writer refuted (0 calls).
H3a: bulk copy/memset/DMA of the array; H3b: direct sb in other function with different base reg; H3c: script interpreter writes by computed address.
Discriminator: env-gated hook on every guest byte store into 0x8013889F..0x8013891F with PC (rs64_probe_submit_gate_store already sees 'B' stores — check if it carries range+PC for all sb sites), positive control = watch fires for id 0x20 first write. Then fold s5688_bool7_b and one failing-arm soak.
HYPOTHESIS-ID: g1-bool7-voice-path
