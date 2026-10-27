# NEXT: EMPTY rate per table per arm over ALL keys (mission table 802EE7B4 first)
HYPOTHESIS-ID: g1c-span-reject-predicate

s6517: table base = level image from load_level_hmp (80246434 keys 1-130,
802525E4 keys 131-744, mission 802EE7B4 keys 745+), same in dd1 and dd4. The
s6516 "different table" was a sampling-phase confound (dd1 EMPTY rows keys 2-8,
dd4 EMPTY rows keys 399-499).

Hypotheses: H-mission-differs (dd4 EMPTY rate on 802EE7B4 > dd1), H-phase-only
(EMPTY occurs only during load phases 1-2, harmless to flight), H-gate-hides
(the [span-filter] dump gate hides mission keys, so no EMPTY data exists there).
Single build: find the dump gate near the "emp" computation in funcs_9.c
(~line 14777, emptydump); make [span-filter] print a one-line summary for EVERY
keyed return (key, emp, table d4, npass/nskip/nclear), then count EMPTY/ok per
table per arm. Reuse scratch/agent/s6517_desc_owner.sh with s/s6517/s6518/.
Control: ok+EMPTY rows total == desc-ent count per arm.
