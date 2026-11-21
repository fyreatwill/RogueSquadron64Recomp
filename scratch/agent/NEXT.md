# NEXT (s7781; s7780 repaired the s7779 census contract, unit below still unrun; s7779 closed dangling-global class item 31 7/7: the FRAME member is retail's frame-scoped FB scratch arena)
HYPOTHESIS-ID: fb-arena-escape-class
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Class (idiom audit, item 3 of ITERATION.md): retail rs_malloc(size, flags&4) allocates from a scratch arena (head 0x8010FEFC) built by
ensureHeapInitialized over a FREE framebuffer (acquireFreeBufferSlot 0x8001C07C, which does not mark the slot busy). clearFrameReadyFlag
(0x80001880, from beginSceneRenderFrame) drops the arena WITHOUT freeing its blocks. Any pointer into an arena block that is used after
its epoch ends points into a framebuffer that the RDP will draw over: a retail-latent use-after-free (or a port-only one if our epoch
timing differs). s7779 measured epochs of 10-70 ms on owner route_long (10 per run) and 0 foreign host writes inside them.

Hypotheses:
- H-clean: every flag-4 caller is done with its block before the epoch ends (inflate workspace, loader temp buffers).
- H-escape: some flag-4 block pointer is stored in a resident/heap global and used after the epoch (guest stores/loads into the
  closed extent by non-FB code).
- H-port-timing: escapes only in the port, because a beginSceneRenderFrame happens mid-load (our thread scheduling), so the epoch
  closes before the loader finishes.

Unit, ONE build, ONE run:
1. Static: enumerate every rs_malloc call site in the retail ELF whose a1 has bit 4 set (constant a1 at the jal delay/before it;
   mips64-elf-objdump of rogue_squadron64/build/roguesquadron.elf, the same live-reg walk as tools/s7335_fb_bound_census.py). Classify
   each caller: where the result goes (stack/local, resident global, heap struct), and whether it frees it before returning.
2. Runtime: extend the s7779 path (src/main/main.cpp rs64_s7779_note). On each live->0 transition, remember the closed extent. Count
   GUEST stores into it until the next epoch per pc (s6843 sees only stores). Optionally use the s7777 load watch (ROGUESQ_STORE_DIAG) on
   the extent for loads. Split the pcs into FB writers (CPU framebuffer draws, if any) and everything else. Any loader/inflate pc
   storing into a closed extent = H-escape. Then check whether a beginSceneRenderFrame fell inside that load: if it did and retail
   would not (H-port-timing), the epoch-close order is the question.
   Positive control: a planted store (ROGUESQ_S7780_PLANT, host-side call of the guest-store note with a fake pc into the last closed
   extent) must be counted; the in-epoch guest store count (1780/run in s7779) is the live control.
Run: `zsh tools/s7774_slot_run.zsh s7780a ROGUESQ_S7779_ARENA=1 ROGUESQ_S7779_PLANT=300 <new flags>` (owner route_long, 300 s).
Score with tools/s7779_arena_score.py extended with the escape table (rc 0 H-clean, 1 H-escape, 3 control fail).
