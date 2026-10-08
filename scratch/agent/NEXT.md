# Next work unit: kill the residual 7% ODD cimg + qualify the KEEP_PIPE fix (s4273)

HYPOTHESIS-ID: m5-audio-destub-sequence

Context (s4272): bump-time content of 8-byte DPC submits is a placeholder (2F/E7); final triangle words land after the DPC_END bump. The E7 drop in rsp_dpc_submit deleted future triangle data (ODD cimg 61% -> 7% with ROGUESQ_DPC_KEEP_PIPE default ON). Tools: scratch/agent/s4272_ab.sh (arm0/arm1 sequential), ROGUESQ_S4272=1 shadow-diff (`[s4272-latewrite]`, `[s4272-latetot]`), ring/list dumps `[s4271-ring]`, `[s4271-list]`.

Hypotheses for the residual ~98 ODD:
- R1: other bump-time 8-byte filters (0xFF cimg suppress `s_suppress`, `gate_inject` F3/FD/F5 drop) delete placeholder-slot words.
- R2: multi-word bumps whose content is still placeholder at commit (DMA lands after task end).
- R3: legitimate odd-looking cimgs.
Discriminator (one build, one run): per-filter drop counters keyed on whether the dropped word's commit-time value differs from its bump-time value (use the existing shadow); positive control = KEEP_PIPE=0 arm must show the E7 filter with diffs > 0. If an R1 filter has diffs>0 -> move it to commit time. Then run the hangar reach/crash soak (s1949 recipe) with the default fix to see if crash families (filterVoiceSampleBlock+220, waitForAnyAudioSlot) change; resume M5 plan Step 9/10.
