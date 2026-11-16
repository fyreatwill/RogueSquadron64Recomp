# NEXT (s7425)
HYPOTHESIS-ID: build-option-drift

Class CH (CURRENT-TRUTH Next steps item 1): s7424 proved every linked object is current with the live source. Are the OPTIONS it
was compiled with the intended ones? Offline only.
1. Enumerate every option()/cache variable in CMakeLists.txt (ROGUESQ_* at lines 27-423: NO_ITER_DEBUG, DX12_DEBUG, RT64_OPT,
   PLUME_OPT, FB_LDWATCH, SP_WATCH, UCODE_NO_OPT, TSAN_UCODE, SRC_OPT, FUNCS_OPT, plus RS64_BYTE_WATCH at line ~102 and any
   RECOMP_FUNCS_DIR / N64RECOMP_EXE / MIPS_GCC path vars) with its default; read build/CMakeCache.txt for the value in force.
2. Per linked object (compile_commands.json, s7424 closure): extract -O level, -D defines, -fsanitize, -g; group by target. Flag:
   diagnostic defines on (RS64_BYTE_WATCH, FB_LDWATCH, SP_WATCH, TSAN), -O0 where an *_OPT option says -O2, objects whose flags
   differ from their target's flags.make (stale flags), cache values differing from defaults without a documented reason
   (grep CURRENT-TRUTH/OWNER-OPT-INS for each).
3. Cross-check against the binary: `nm` for watch/tsan/asan symbols (e.g. __tsan_*, __asan_*, rs64 byte-watch hooks) so a define
   claimed off is also absent in the linked image.
4. Positive control: a planted compile entry copy with -DRS64_BYTE_WATCH -O0 must be flagged; a planted cache value != default must
   be flagged.
Hypotheses: H-intended (every option at its default or a documented choice; no diagnostic define in the shipped build) vs H-drift
(>=1 undocumented non-default / diagnostic flag live; then say what it costs: frame time, behaviour, and whether to reset it).
Write tools/s7425_build_options.py. Exit 0 = intended, 1 = drift, 3 = control failed.
