# NEXT: read-side watch of words 0..7 of chunk-2+ voice records
HYPOTHESIS-ID: m5-audio-destub
Established (s4574): words 0..7 of voice records are never written by render code, only by bulk fills (0x8001E2C0/E2F0/21EB4); chunk-2+ words 8..33 use the same render PCs as in-range. H-offset0-7-render and H-hostzero refuted.
Hypotheses: H-inert (no PC loads words 0..7 of chunk2+ records, residue harmless, close the thread), H-read-wild (a render/synth PC loads words 0..7 as a pointer, so the ASCII residue is a live crash source; name the PC and its use).
Discriminator: one build adding load counting by (cls, word, PC) to the same table (find the load hook next to the rs64_s4572_note callers in upstream_compat.cpp; add one via the apply_s4572 pattern if none exists). Positive control: loads of in-range words 8..33 by render PCs must print. Reuse scratch/agent/s4574_build.sh and s4574_storewatch.sh (copy to s4575), analyze with s4574_an.py.
