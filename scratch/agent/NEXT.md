# NEXT (s7597)
HYPOTHESIS-ID: uncaught-exception-census

Class FS closed s7596 (20 throwing rows, 0 open; stored-ROM remove + current_path fixed). Class XC = every OTHER host call that
can throw a C++ exception out to std::terminate in owner-reachable code (src/, librecomp/src, ultramodern/src, lib/rt64/src;
skip tests/tools/contrib/examples). Raw counts at s7596: json::parse 4, explicit throw 10, .at( 15, std::thread ctor 67
(std::system_error on thread-creation failure), plus nlohmann .get<>/operator[] on const json, std::bad_alloc on huge new.
Per site: reachable (boot / play / quit / env-gated / dead); inside a try?; what input makes it throw (malformed config/manifest
JSON, missing key, out-of-range index from guest data, thread limit); consequence.
Hypotheses: H-clean (every reachable one is in a try or cannot fire), H-crash (an owner-reachable abort like FS-1: e.g. a
malformed config file aborts boot), H-guest (a guest-data-indexed .at() can throw in play).
Tool: tools/s7597_xc_census.py --controls (plant an untried json::parse + drop a row; both caught). Runtime witness for each
H-crash row in copied folders (pattern scratch/s7596/run.zsh): old arm aborts, fixed arm alive, ctl alive.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
