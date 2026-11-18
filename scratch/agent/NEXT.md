# NEXT (s7596)
HYPOTHESIS-ID: throwing-filesystem-census

Class SV closed s7595 (21 rows, 0 open; throwing create_directories in read_save_file/initialize_mods aborted boot, fixed).
Class FS = every OTHER throwing-form std::filesystem call (no std::error_code argument) in src/, lib/N64ModernRuntime/librecomp/src,
ultramodern/src and lib/rt64/src (tests/tools/demos skipped). ~30 raw grep hits at s7595:
  grep -rn -E 'std::filesystem::\w+\(' ... | grep -v error_code/ec
Per site: reachable in the owner's run (boot, shader cache, texture packs, dumps, logs) or env-gated/dead; surrounded by try/catch?;
what input makes it throw (missing dir, permission, a file where a dir is expected, non-UTF-8 path); consequence (terminate vs caught).
Hypotheses: H-clean (every reachable throwing call is inside a try or cannot fail), H-crash (another owner-reachable boot/run abort
like SV-1), H-gated (the throwing ones sit only behind diagnostic env flags).
Tool: tools/s7596_fs_census.py --controls (plant one throwing call in a reachable function + drop a row; both caught). Runtime witness
for each H-crash row: the s7595 copied-folder pattern (scratch/s7595/run.zsh: symlinked binary+ROM, COPY of the owner save,
NO_SAVE_WRITE=1, boot-only), pre-fix arm aborts, post-fix arm alive, same-binary old-arm env as control.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
