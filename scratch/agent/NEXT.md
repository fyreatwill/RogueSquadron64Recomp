# Next work unit: hangar entry-frame DL/source-data byte diff, retail vs port

HYPOTHESIS-ID: hangar-artifact-triage

s4506: retail+Rice never writes the RDRAM framebuffer (title control 0 words, hangar fb 0 px) -> no pixel diff.
Hypotheses: H1 colour/texture-format on specific materials; H2 bad vertex/DL data; H3 LLE ucode divergence;
H4 fb width/stride mismatch (right-edge column).
Discriminator: at the hangar entry (VI 512, origin 0x6AB400) dump from BOTH retail (oracle --fb-dump raw RDRAM,
or --pc-task-dump for the OSTask row) and port: the gfx OSTask data_ptr DL bytes + vertex/texture ranges it
references; byte-diff. Identical source + bad pixels => H3/H1 in port renderer; differing source => H2 (guest state bug).
Positive control: diff the same procedure on title (1024) task, expect identical.
Cheap side item for H4: port-side log VI_WIDTH vs colour-image width at hangar.
Tools: tools/oracle/rs64_oracle --fb-dump, --pc-task-dump; scratch/agent/s4506_oracle_fb.sh as template. One run at a time. SIGKILL.
