# Next: decide H1 (host load) vs H3 (generated code) for the nohangar stall
HYPOTHESIS-ID: m3-idiom-class-audit
s5051: restored-tree rebuild still stalls (nohangar t=200, last origin 0x696100) with load avg 5-7, Chrome 108% CPU.
Needs a quiet host. Ask the human to quit Chrome/REAPER, then run `zsh scratch/agent/s5048_preS5038_source.sh` (check load <2 in keys1.log). Hangar reached = H1 (host load); stall again = H3 (generated code).
If the host cannot be quieted, use a known-good older commit's build as a same-host positive control.
Never run tools/agent/regen_n64recomp.sh or regen in place.
