/* Symbol bindings for patches. Two kinds of entries:
 *
 *  1. Game-side functions/data the patches need to reference. These resolve
 *     to addresses in the original ROM. Add as we need them.
 *
 *  2. Runtime stubs at fake absolute addresses (0x8FXXXXXX). N64Recomp
 *     recognises these and emits direct calls into librecomp/host code.
 */

__start = 0x80000000;

/* --- Runtime stubs (host code callable from patches) -------------------- */
/* (none yet — populate when we need them) */

/* --- Game functions called from patches --------------------------------- */
/* The C patch and assembly use this absolute linker alias; N64Recomp maps the
 * matching relocation to the game's reference symbol by name. */
func_8002221C = 0x8002221C;

/* --- Game data symbols touched by patches ------------------------------- */
/* heap_guards.c reads/writes these globals. Addresses are static RAM slots
 * in the original game's BSS.
 *
 *  heap_free_head      (Block*)   the head of the heap's free list
 *  heap_other_listhead (Block**)  pointer to the active-queue head slot
 *  heap_tail_loc       (Block**)  pointer to current tail-node slot
 *  heap_bump           (void*)    bump-allocator pointer (popped + 0x100)
 */
heap_free_head      = 0x801163B0;
heap_other_listhead = 0x801163FC;
heap_tail_loc       = 0x8011A7DC;
heap_bump           = 0x801163D4;

/* cinematic_probe.c (s6269 patch qualification) */
cinematic_flag = 0x800B0934;

/* rng_patch.c (s6277 patch qualification) */
rng_seed = 0x80003470;

/* dl_finder.c (s6278 patch #3) */
dl_bucket_count = 0x80128EF0;
dl_used_head    = 0x80128EF8;
dl_buckets      = 0x80128F00;
