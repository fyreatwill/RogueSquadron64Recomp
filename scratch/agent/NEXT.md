# Next work unit: name the writer of the zeroed allocator head (s4278)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4277: 8/9 s1949-recipe runs crash with `[s4230-FD60] head=0 tail=801F9D10` then fillSampleStreamRange+9264 far=0x380000000; audio ucode (silent) and private DMEM do not matter.
Hypotheses: H1 early Start presses (6 s onward, during intro/attribution) trigger a state the 40 s+ routes never hit; H2 a post-s1950 source/default change zeroes the head; H3 an RS memset/free path legitimately clears head while tail stays (port-only lowering).
Discriminator (one build, one run set): add a host watch on the head word (see tools/apply_s4234_entryprobe.py) logging the guest PC of every write between ENTRY n=9400..9507; arms in one batch: (a) s1949 keys from 6 s, (b) same recipe with keys from 40 s. Positive control: the watch must fire on a known head update before n=9506. Outcome splits: writer PC in memset/clear -> H3; crash only in (a) -> H1; both crash -> H2 (bisect commits since s1950).
Scripts: scratch/agent/s4277_bisect.sh (template), s4277_count.sh (breadcrumb counts).
