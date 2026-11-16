# NEXT (s7488)
HYPOTHESIS-ID: m3-unaligned-store-uaf

s7487 closed EL on L4/L15 (lwl/lwr: 0 freed-block reads, LWLCTL plant DETECTED in flight on both). Levels soak s7487_lwlwatch_levels
(L1 dd8 21:9, L7/L10/L12 dd4) is queued: fold its verdict first (score=0 -> EL closed for 6 levels; any lwl_F/lwl_Urec -> chase the
`[s7487] lwl-hit` row: pc, blk, loc).

Work unit (class EM): guest UNALIGNED STORES swl/swr (405 generated sites: 203 swl + 202 swr; 404 carry the s5660 hook
`rs64_s5660_ustore(pc, addr & ~3u, 0, 'L'|'R')` in src/main/main.cpp:2152). That hook never reaches rs64_s7475_store, so the s7475 canary,
s7479 pad and s7480 UAF store watches (classes ED/EG/EH) are blind to swl/swr. Steps:
1. Census: find the 1 swl/swr site without the s5660 hook (grep `// 0x...: swl|swr` vs `rs64_s5660_ustore`), and any sdl/sdr.
2. Pass the exact written bytes: the hook only gets the aligned word. Either a new fixup tools/apply_s7488_ustorewatch.py that inserts
   `RS64_S7488_ST(pc, base, imm, isl)` before each do_swl/do_swr (swl at a writes [a, a|3], swr writes [a&~3, a]) with the same bitmap test
   as RS64_S7484_LD, calling rs64_s7475_store(pc, lo, w, __func__) on a marked byte, gated on a new g_rs64_s7488_on
   (ROGUESQ_S7488_USTOREWATCH=1 under S7475_CANARY+S7480_UAF). Regen order make_elf -> N64Recomp -> fixup_game_funcs -> cmake (or run the
   idempotent script on RecompiledFuncs + register it after apply_s7487_lwlwatch.py, as s7487 did).
3. Census counters like s7487 (exec per site, sampled live-heap hits) and an EM control ROGUESQ_S7488_USTCTL=<s>: record as freed a live block
   an swl/swr just wrote; the next swl/swr into it MUST log `[s7488] ust-ctl DETECTED`.
4. Recipe: copy tools/s7487_lwlwatch_recipe.zsh, LV="4:4 15:8" HOLD=220; score EM on canary slack-store rows from swl/swr pcs and s7480 F/Urec rows.
Hypotheses: H-ust-clean (0 slack / F / Urec stores from swl/swr, control DETECTED) / H-ust-overrun (a canary slack-store or tail hit from an swl/swr pc:
names the writer) / H-ust-uaf (F rows) / H-ust-none (sites never write heap in flight: close as vacuous with the census).
