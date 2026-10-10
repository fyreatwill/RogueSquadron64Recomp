# NEXT: aligned hangar entry-frame comparison (H3: raster/VI/colour image) — counts already agree

HYPOTHESIS-ID: hangar-artifact-triage

s4516: retail with the port's 11-Start schedule shows entry frame texrect 0/tri 1244, then 195 texrects/tri 1103-1140 (sync 1618+); port s4515 (195/1120-1130) matches the later band. H1b unsupported.
Hypotheses: H3a port draws the same RDP stream but raster/RT64 output wrong (rim band, spikes); H3b VI/colour-image width (right-edge column); H1c same counts but different vertex values (not visible in counts).
Discriminator: in ONE port run, dump the raw RDP stream for the first VI-512 sync (the 0-texrect entry frame; use fewer Starts or phase-gate capture at the first sync after VI 512) and byte-diff the triangle edge-coeff words against retail's s4514 rdp.bin / s4516 rdp.bin (RS64_RDP_BIN, width 512 syncs 1515-1516). Equal bytes => H3a/H3b (rendering side); differing triangle words => H1c (vertex transform). Positive control: title 1024 sync byte-identical or texrect count 161 on both.
Note: tools/oracle/rdplog/rdplog.c record format {RDPC,vi_origin,vi_width,nbytes,seq,words}; port needs an equivalent dump hook at the dpc_bridge.
