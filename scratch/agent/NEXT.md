# NEXT (s7319): close class B — fold the s7318_bcmp_levels soak, then statically classify the sites no run executed
HYPOTHESIS-ID: spill-holder-field-compare
Context: s7318 runtime classifier (ROGUESQ_S7318_BCMP, tools/apply_s7318_bcmp_probe.py): dd8 21:9 L4 250 s flight, 109/182 class-B sites
executed, 0 cross compares (spill pointer vs 0x80xxxxxx), control 2569/2569; the 464 spill-operand compares are zlib window pointers
in one block. 73 sites never executed (list: `python3 tools/s7318_bcmp_report.py scratch/s7318/bcmp_run1.txt scratch/s7318/bcmp_run2.txt`).
Soak scratch/agent/soak_queue/s7318_bcmp_levels.sh (L1 + L12) queued; its tables land in scratch/s7318q/bcmp_l{1,12}.txt.
Hypotheses for the remaining sites: H-scalar (the compared field is a count/size/time, never a pointer) vs H-same (pointer vs pointer
into the same object/array) vs H-cross (a pointer vs a heap bound/pointer from another allocation -> can misorder a spill pointer).
Unit:
1. Fold the soak verdict (SOAK-RESULTS). Re-run the report over all 4 tables; any cross -> read that function first (that is the unit).
2. For every still-unexecuted site: read the lw/slt pair and the surrounding 20 lines in N64Recomp/RecompiledFuncs (grep the pc), and
   class it H-scalar / H-same / H-cross / by-construction (heap freelist walkers never see spill: the spill arena is its own allocator;
   __osPfs* is controller-pak code with no heap pointers). Write the table into docs/HEAP-ADDR-AUDIT.md (class B section).
3. If any site is H-cross on a field an owner type in scratch/s7317/d8_owner_table.txt actually holds: name the compare's meaning and
   fix (allocate that owner type outside the spill arena, or map the compare), qualified with the two-arm discipline.
Outcomes: all scalar/same/by-construction -> class B CLOSED, spill-holder thread closed; take CURRENT-TRUTH Next steps 16.
