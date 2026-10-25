# G1d: why does the up_167 TMEM upload (h98bb35b7e7c80445) contain noise when its RDRAM source looks like photo?
HYPOTHESIS-ID: g1d-widescreen
s6234: the noisy texture is drawn 6x/frame at title (0 misses). H-up167 supported. Hypotheses: H-load (LoadTile addr/dxt/line wrong so TMEM load reads wrong RDRAM), H-stale (RDRAM source overwritten between LOADBLOCK parse and upload), H-tmem (RT64 TMEM load/word-swap at that call).
Next: in queueGPUUploadTMEM (rt64_texture_cache.cpp) when hash==ROGUESQ_LOG_TEXHASH log LoadTile fields; in the same run read RDRAM at that address (via rsp/rdram pointer) and compare to `bytes`. Control: same compare on a clean upload must match. Run: zsh scratch/agent/s6234_run.sh 900 log (background, ~10 min).
