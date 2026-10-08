# Next work unit (s4292): bisect the 640->1024 boot slowdown

HYPOTHESIS-ID: m5-audio-destub-sequence

s4291: title at ~52 s (s1949: 14 s); no 512 with either key schedule.
Hypotheses: B1) DPC_WRAP_FLUSH/wrap-restore cost; B2) S4271/S4272/S4268; B3) a regression since s1949; B4) missing M4_Y8000_WIDTH=512 / LOG flags.
Discriminator: copy scratch/agent/s4291b_hangar_ab.sh into 3-4 concurrent arms each differing by one flag; compare [phase] 1024 time. Control: baseline arm still ~52 s.
