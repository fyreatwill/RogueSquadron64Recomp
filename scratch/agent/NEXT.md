# NEXT (s7467)
HYPOTHESIS-ID: host-analyzer-rest

s7466 closed DT (soak PASS) and DV (tools/s7466_analyzer_rest_census.py --controls rc 0, 2 fixes, 4 reviewed). The clang
single-TU analyzer families are now exhausted for the 150 host TUs.

Next unit (class DW): cross-TU / runtime coverage the single-TU analyzer cannot see. Hypotheses: H-asan-clean (an ASan+UBSan
build of the owner recipe, L4 + L12 dd4 HOLD=150, reports 0 errors) vs H-asan-hit (a heap/UB error the analyzer missed, named
by its stack). Discriminator: one separate build dir (build-asan, -fsanitize=address,undefined -fno-omit-frame-pointer), one
queued soak with both arms + a planted control arm (env ROGUESQ_S7467_ASAN_PLANT=1 does a 1-byte heap overflow once at boot,
must report). Check first whether a build-asan already exists (grep PORTING-STATE "build-asan"), reuse its recipe.
If ASan was already run on this recipe recently with a control, take the next ladder rung in ITERATION 3c instead.
