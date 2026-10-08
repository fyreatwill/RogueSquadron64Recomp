# Next work unit: resume the M5 audio de-stub sequence (docs/M5-AUDIO-PLAN.md) at its next unexecuted step

HYPOTHESIS-ID: m5-audio-destub-sequence

s4234: the allocator head==0/tail!=0 corruption did not recur in 4 runs (~80k entries); ra==0 at fillSampleStreamRange entry is normal. That thread is parked wait-for-recurrence (probe in tools/apply_s4234_entryprobe.py; recipe scratch/agent/s4234_entry.sh). Do NOT spend another iteration on it unless a soak shows head==0 with tail!=0.
Do: read the "Validation row required for every step" section and the ordered step list of docs/M5-AUDIO-PLAN.md, pick the first step not marked executed, state the competing hypotheses and discriminator here before building, then run it with a same-run positive control.
