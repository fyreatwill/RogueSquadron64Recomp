# NEXT (s7487)
HYPOTHESIS-ID: m3-unaligned-load-uaf

s7486 closed EK on L4/L15 (host readers of freed heap: 0 F/Urec, host plant DETECTED in flight on both). Levels soak
s7486_hostuaf_levels (L1 dd8 21:9, L7/L10/L12 dd4) is queued: fold its verdict first (score=0 -> EK closed for 6 levels; any
host_F/Urec row -> chase it: the row names kind, block, free arena, plus read-bt/free-bt).

Work unit (class EL): guest UNALIGNED loads lwl/lwr/ldl/ldr, the gap EI left (tools/apply_s7484_loadwatch.py line 9: do_lwl helpers
not wrapped). Grep the RecompiledFuncs for the do_lwl/do_lwr/do_ldl/do_ldr call shape, count the sites, and wrap them with the same
RS64_S7484_LD bitmap test (address = the aligned word(s) actually read). Regen order: make_elf -> N64Recomp -> fixup_game_funcs -> cmake
(the wrapper runs inside the fixup chain). Recipe: tools/s7484_uafload_recipe.zsh with LV="4:4 15:8" HOLD=220. Control: the s7484 load plant
must still be DETECTED. Add an EL-only control as well: with ROGUESQ_S7487_LWLCTL=1, mark one known lwl source (pick from the site census)
and check that it logs.
Hypotheses: H-lwl-clean (0 F/Urec from unaligned loads) / H-lwl-uaf (F rows name pc + freeing caller) / H-lwl-none (0 lwl sites execute in
flight: report the site census and close EL as vacuous with the census as evidence).
If the census shows 0 generated lwl/lwr sites, close EL offline and take the next ladder item.
