# Next work unit

HYPOTHESIS-ID: rt64-opt-frame-limiter

s4909: VI-queue recv trace shows tid 0 blocking twice per swap (host wrapper only). Parked as host-slow frame (s4903/s4907). Do NOT add more recv fields.

Next unit: make the rt64 -O2 build default (s4907) and re-measure swaps/s with scratch/agent/run_s4908.sh arm A. Discriminator: swaps/s -> ~60 means 30 Hz was purely host cost (H-host-slow confirmed, close thread); stays 30 means a guest divider exists (then read recv guest ra via a guest-PC thread-local). Control: arm B sleep10 must lower swaps.
After that, resume M5 audio plan (docs/M5-AUDIO-PLAN.md).
