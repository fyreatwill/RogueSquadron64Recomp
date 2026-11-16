# NEXT (s7492)
HYPOTHESIS-ID: m3-store-path-coverage

Fold first: soak s7491_ep_levels (L1 dd8 21:9, L7/L10/L12 dd4; tools/s7491_ep_recipe.zsh). score=0 + mplant DETECTED fn=os_* on all
arms -> EP CLOSED for 6 levels. Any os_* uaf-store row with loc=F/R: chase it (fn names the OS call, a= the destination).

Work unit (class EQ, the remaining host guest-memory writers that bypass MEM_ macros, named in s7491):
 (a) ultramodern thread-queue link writes: thread_queue_insert/pop/remove write mq->blocked_on_recv/send and OSThread->next/queue
     (lib/N64ModernRuntime/ultramodern/src/threadqueue.cpp or threads.cpp; grep `->next =`, `*queue =`). Add RS64_S7491 kinds
     os_tq_link / os_tq_head (extend k_s7491_kind in src/main/upstream_compat.cpp, S7491_NK) after each write.
 (b) osPfsNumFiles (librecomp pak.cpp) `_arg<1, s32*>` host-pointer stores: check whether _arg<N, T*> returns a correctly swapped
     guest pointer at all (it may write host memory at the wrong place = a real defect); hook or fix.
 (c) RT64 framebuffer readback into guest RAM (RENDER_TO_RAM path, lib/rt64): enumerate the write sites; route them as kind rt64_fb.
 Then: ./submodule-patches/export.sh, extend NEED in tools/s7490_hostwrite_census.py, rerun tools/s7491_ep_recipe.zsh LV="4:4 15:8"
 HOLD=220 with an in-flight control (MPLANT_S ~ 120 so it lands after initMission).
Hypotheses: H-eq-clean (0 F/Urec/slack rows) / H-tq-uaf (a thread queue links a freed OSThread or mq) / H-pfs-wild ((b) writes host
memory outside rdram; single read of the _arg template decides).
If EQ closes clean, the M3 heap-audit store/load series is DONE: take the ITERATION 3c ladder's next open rung (G5 owner items are
owner-look only; check CURRENT-TRUTH Next steps 2-9 for anything with an engineering action).
