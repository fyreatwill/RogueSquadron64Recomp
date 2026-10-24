# NEXT: G1d step 21 - who creates the 0x2DB000 (ctl) / 0x3E4B00 (21:9) main-heap block, and what grows the ctl heap end 0x80769FF0 -> 0x80795BF0?
HYPOTHESIS-ID: g1d-widescreen
Known (s6128): rs_malloc stream identical wide vs ctl; the largest used block differs (+0x109B00) and no logged rs_malloc has its size, so it comes from an unlogged path (pool/FB layout inner call, split/coalesce). Heap end lower in wide.
Hypotheses: H-pool (a width-scaled pool carved via inner alloc), H-split (free-tail merged into a used block), H-heapend (initMainHeap end derived from fb layout; ctl extends it later).
Discriminator: in the s5041 wrapper log ra/size for ANY inner call with size>=0x100000 and log heap-end sentinel writes (0x80795BF0 / 0x8071B670 stores) with guest pc; run wide + ctl (recipes as s6128: ROGUESQ_HEAPLOG=1, XENV_EXTRA ASPECT=21:9 vs none, HOLD_S=30 LEVEL=1).
Outcome: creator named -> size it from width or move it above 0x80800000; heap-end writer named -> fix extension for wide.
