Single next work unit (s5620): fold s5618_nopoke_c + s5618_poked_ctl (run with the s5619 binary).
Method: grep -h '\[hudbit\|\[cco\]' scratch/agent/m6/s5618_{nopoke_c,poked_ctl}/run.log. ra is ALWAYS 0 (static jal never sets r31) - identify the caller by the [cco] lvN line immediately preceding each [hudbit] line.
Positive control: poked_ctl must log >=1 [hudbit] line, else nopoke zeros mean nothing.
Outcomes: [cco] lvN precedes hudbit4 => H4a-i confirmed, level N is the mission; no [cco] before => script call (H4a-ii); gate 4 with no hudbit => H4c, find writers of 0x8010CA20.
HYPOTHESIS-ID: m6-mission-endurance
