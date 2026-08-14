# NEXT work unit (s946)

Pre-run decision: source-only; do not build, run the game, or enqueue a soak.
The discriminating measurement is an exhaustive reachability inventory for
the standalone allocator body at `0x80086450`: no reachable edge or a proven
voice-record argument at every edge selects valid; a non-voice argument
selects mismatch; an unresolved target or argument selects unclassified.

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit reachability of the standalone `allocVoiceHandleNode` body at
`0x80086450` and distinguish it from the three already classified inline
insertion/reuse bodies. Inventory every direct call, every audio-overlay
`jalr` candidate, and the register/value setup at each candidate; cross-check
companion symbols. No guard, behavior change, build, or soak.

Competing hypotheses:

- H-stop-voices-by-handle-index-valid: the standalone body is dead or every
  reachable dispatch supplies the same live voice-record contract as the three
  inline sites.
- H-stop-voices-by-handle-index-unclassified: a candidate indirect edge or
  standalone caller remains unresolved.
- H-stop-voices-by-handle-index-mismatch: a reachable standalone edge supplies
  a non-voice record or incompatible handle/state value.

Discriminating measurement: exhaustive generated-source inventory of all
`0x80086450` direct references and audio-overlay `jalr` target setup, plus the
companion-symbol cross-check. No reachable standalone edge, or a proven
voice-record argument at every edge, selects valid; a non-voice argument
selects mismatch; an unresolved target or argument selects unclassified.

Exact command: `rg -n -C 10 "80086450|allocVoiceHandleNode|jalr|0x80085C70|0x80086524|0x80086E40|0x8008738C|0x800877E0" ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then classify every candidate edge. No game build or soak is planned.
