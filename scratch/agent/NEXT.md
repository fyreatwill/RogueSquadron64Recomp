# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4869: per-voice work per walk matches (11.74 vs 11.80 jals); the split is chunks per synth entry: walk 0x80090E04 is called once per 0xC0-sample chunk (sites 0x800914C8/0x80091588/0x8009163C; s2+=0xC0, s3+=1). Retail 1.91 walks/entry, port 1.01 per real entry (spurious entries: none).
Hypotheses: (H-T) chunk loop bound/target (derived from AI drain / ring state read at ~0x80091398-0x800914B0, e.g. halfword 0x80149988-style consumers) is ~2 chunks in retail, 1 in port because AI consumer drains less per frame in port; (H-U) same bound but the loop exits early in port (flag/branch); (H-Z) second chunk happens through other call sites 0x80091588/0x8009163C (124+40 = only 164/1341 in retail, so minor).
Discriminator: read the loop control (compare of s3 vs limit near 0x800914D0-0x80091540; use grep of funcs_24.c lines 7540-7720) then log the limit/start values at the loop head in port (funcs_24 hook, template apply_s4871_voices.py; helper only in one file) and in retail by extending tools/oracle/rs64_oracle.c to print s2/s3/s4/s5 (do NOT watch delay-slot PCs; 0x80091084 gave 0 hits). Same limit -> H-U; limit 2 vs 1 -> H-T, then trace its writer.
