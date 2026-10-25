# G1d: which loads compose the noisy up_167 TMEM (h98bb35b7e7c80445)?
HYPOTHESIS-ID: g1d-widescreen
s6235: no single LoadBlock >=1KB reproduces up_167 TMEM; matcher control passes (clean uploads match). Hypotheses: H-multi (several small loads assemble it; one carries noise), H-stale (a later load overwrites part of TMEM before upload), H-tmem (RT64 upload/word-swap).
Next: in uploadTexture/queueGPUUploadTMEM log g_rs64LoadSeq at upload for hash==ROGUESQ_LOG_TEXHASH; offline list the last ~16 loads (tmem range, src addr) before it, and diff each load's tmem dump vs the up_167 bytes at that range. Run: zsh scratch/agent/s6235_run.sh 900 log (loads in scratch/agent/m6/s6235_log_w900).
