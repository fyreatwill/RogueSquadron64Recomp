# NEXT (s7340): idiom-class audit - class O, host KSEG0 16 MB upper bounds (`0x81000000` / `0xFFFFFFFF81000000`) vs spill pointers
HYPOTHESIS-ID: kseg-16mb-bounds
Context: s7339 closed class N (16 MB masks, tools/s7339_mask16_census.py, B 0) and widened the sp.cpp wrapper guard to
max(0x81000000, rs64_ram_top). The spill arena is 0x81000000-0x81800000 and rs64_ram_top reaches 0x81800000 (s7336). Any host
validator `a < 0x81000000` / `a >= 0x81000000 -> reject` that runs default-on on a guest pointer drops spill-resident objects.
Count (s7339): upstream_compat.cpp 50, sp.cpp 7 (now the s7339 bound), main.cpp 2, s7324_rcp_spill 1, dpc_bridge 1, overlays 1.
Hypotheses: H-diag (gated audits: s7317/s7318/s7333/g5a walkers bound the GUEST heap on purpose), H-reject (a default-on
validator rejects a spill pointer: silently skips work), H-intended (bound means "guest heap only" and spill is handled by a
separate branch, e.g. s7324_class).
Method: copy tools/s7339_mask16_census.py's frame with an `0x(FFFFFFFF)?81000000` regex; classify by enclosing function; any
H-reject site -> rs64_ram_top bound behind ROGUESQ_S7340=0 with a hi counter; runtime: `env SECS=260 zsh scratch/s7326/run.zsh
s7340_dd8 ''` (spill live; control = a selftest predicate on 0x81000100 as in s7339).
