# Next work unit: child-DL dump + structural compare (hangar VI 512)

HYPOTHESIS-ID: hangar-artifact-triage

s4509: root DL (0xD8 B) is identical retail vs port; 13 child-DL targets are listed in PORTING-STATE s4509.
Hypotheses: H2 guest child-DL/vertex/texture data differs vs H1/H3 port renderer/ucode with identical data.
Do: extend dump hooks (oracle dump_pc_task in tools/oracle/rs64_oracle.c; port osSpTaskStart hook in src/main/upstream_compat.cpp) to also dump 0x1000 B at each child target, env RS64_GFX_DL_DUMP_DIR. Parse with scratch/agent/s4509_dlparse.py. Compare command histograms and vertex(04)/texture(fd) pointer sets per child, retail vs port; within-side task0 vs task2 is the variance control.
Outcomes: matching structure => H1/H3 (renderer); persistent child differences => H2.
