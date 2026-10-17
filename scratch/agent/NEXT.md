# Next: audit direct j/jal targets that fall in overlay-aliased VMA ranges (M3 idiom class)

lwl/lwr split-pair class closed (s5347). Finding on the way: the main ELF has overlays
aliasing the same VMAs (e.g. 0x800C1960 exists in several sections).
Hypotheses: H1 every direct jal/j into an aliased VMA is generated with overlay-aware
dispatch (or is intra-overlay and thus unambiguous); H2 some jal from main/other-overlay
code targets an aliased VMA and binds to a single overlay's function statically
(wrong callee when another overlay is resident); H3 aliased ranges only contain
overlay-internal calls (class empty).
Discriminator: tools/ census (reuse tools/audit_lwl_lwr_split.py runs()) listing, per
address run (overlay), the VMA span; then every jal/j whose target lies in a span
shared by >=2 runs, tagged by whether caller run == target run. Positive control:
synthetic cross-run jal into an aliased span must be flagged. For hits, read the
generated C call site and how the project resolves overlay funcs. Do not touch lib/.

HYPOTHESIS-ID: overlay-alias-direct-call-audit
