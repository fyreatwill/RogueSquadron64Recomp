# NEXT (s7424)
HYPOTHESIS-ID: stale-object

Class CG (CURRENT-TRUTH Next steps item 1): s7423 proved the live SOURCE carries every behaviour patch. Does the BINARY match the
live source? Offline only.
1. From build/ (cmake): list every object linked into the game target (build.ninja / Makefile link line, or `ar t`/`ls` of
   CMakeFiles/*.dir). Map each to its source path; confirm the source paths for RecompiledFuncs are the live tree
   /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs (not /tmp, not a copy).
2. Per object: source mtime vs .o mtime (and header deps via the .d files); list objects older than any dependency.
3. Orphans: objects with no current source (renamed/deleted funcs_N.c, removed src files) still linked.
4. Positive control: touch-free check — copy one live .c to /tmp with a planted change and confirm the tool flags it when pointed
   at the copy; and confirm `nm` of funcs_9.o lacks a symbol that only the regen funcs_9 has (s6497 capture line is in live? no ->
   pick a symbol present only in live, require it in the .o).
Hypotheses: H-fresh (every linked object is newer than all its deps and from the live path) vs H-stale (>=1 stale/orphan object;
then rebuild that target and say whether a behaviour patch was absent from the running binary).
Write tools/s7424_stale_objects.py. Exit 0 = fresh, 1 = stale/orphan, 3 = control failed.
