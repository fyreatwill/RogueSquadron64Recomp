# NEXT: cap span-bypass accepted cells to cut RSP cost
HYPOTHESIS-ID: g1c-span-reject-predicate
s6536 confirmed same-run: accept-all costs 2.3x sd_wall (126.8 vs 54.6 ms) and 10.5 vs 18.4 tasks/s at dd4 lvl1.
Work unit: add a distance/count cap to the bypass in tools/apply_s6529_spanbypass.py (e.g. ROGUESQ_BYPASS_MAXCELLS, or only bypass reject when cell distance < dd-scaled radius), regenerate via fixup, build.
Discriminator: pinned lvl1 dd4, s6536_toggle.sh recipe with cap values (e.g. 25%/50%/100% of accepted cells) in arms; per cap record g1b sd_wall/tasks/s and fixed-camera terrain fraction. Pick the cap that keeps most of the 0.209 terrain fraction at near-retail task cost. Positive control: cap=100% must reproduce force-phase numbers.
