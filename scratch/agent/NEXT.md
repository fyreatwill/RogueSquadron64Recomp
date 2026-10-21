# NEXT: [mtm] fold s5754 soaks ([mtmst] per-store mask log)
Read scratch/agent/m6/s5754_mtm{a,b}/run.log: grep '\[mtmst\]\|\[mtm\] n='. Control: >=1 [mtmst] line, and every mtm a0=1 preceded by a store setting bit1.
Hypotheses: H1 bit1 set each mission by one periodic setter pc (benign start); H2 several pcs set different bits, only bit1 ever fires in godmode (fail bits gated by HP); H3 no [mtmst] at all => mask written via a path not matched by the regex (indirect/other base reg) - grep stores to 0x8010C9E0 with other offsets (e.g. lui 0x8011 + -0x3620 with base reg != MEM_W(-0X3620,...) form).
Outcome: pc histogram -> name function per pc (nm/funcs grep), find guard of the missing end bit's setter (iron rule 11: name writer).
HYPOTHESIS-ID: g1-nonhealth-fail
