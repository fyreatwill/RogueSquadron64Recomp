# Next: measure the hangar-recipe flake rate on the current binary under normal load
HYPOTHESIS-ID: nohangar-intermittent-flake
Run `zsh scratch/agent/s5048_preS5038_source.sh` 3 more times (one at a time; copy keys1.log between runs; it logs uptime). Host load is NOT a precondition (s5057). If all pass, the earlier 0/8 stalls were transient (record n/N); if any stall, capture keys1.log lastorigin + ps top-5 and compare against the passing runs to find the discriminator. Then resume the prior workstream.
