# NEXT: name the writer of the wild stream pointer (0x380000000) read in fillSampleStreamRange+15156

HYPOTHESIS-ID: odd-dma-alloc-pair

s4545: the s4541 route is NOT reproducible and not a build difference (binary differs by 2 print-helper symbols; the rest is timing). Stop trying to reach the bad jal. The VI-640 fillSampleStreamRange death reproduces 8/8 within 3 s, so use it as the deterministic route.

Hypotheses: H-voice-corrupt (voice struct in the mix loop holds a bad stream ptr written by init/arm path), H-uninit (field never written before first render; reads leftover/garbage), H-host-timing (synth thread runs before init completes - race).
Discriminating measurement: on the 3-s death, dump the voice struct (base, index, +0x00..+0x88) feeding fillSampleStreamRange at entry and check whether the pointer field was ever stored (watch via the existing s4535 voice-store log) - stored by whom (PC) vs never stored. Positive control: the arm voice (0x8018D4A0 idx 0) dumps a sane pointer in the same run.
Batch all in ONE build (patch via a tools/apply_s4545_*.py, not hand edits), run via scratch/agent/s4544_flaky.sh style.
