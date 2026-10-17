# Next: confirm s5098 shape-3 fixes (build clean + hangar/mission soak), then pick next M3 idiom class
HYPOTHESIS-ID: m3-idiom-class-audits

1. Check the s5098 build finished (cmake --build build). Then enqueue a standard keyed-route soak (copy a recent soak_queue/done recipe, e.g. s5094_hangar_unsigned_base_fix) with ROGUESQ_LOG_SCENE_NODE_CACHE_GUARD=1; expect crash=0.
2. Add an s5097-style post-condition in fixup_game_funcs_vendored.py: abort if any funcs_*.c has `uint32_t X = S32(` later used as MEM_x base (regex: `uint32_t (\w+) = S32\(` then `MEM_\w+\([^,]+, \1\)`).
3. Next class: bare `int`/`unsigned` locals as MEM_x base in other fixup-emitted code (audit_bare_base_types.py shows none today; re-run after regen).
