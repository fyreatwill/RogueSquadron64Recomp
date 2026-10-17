# Next: H1 vs H3 on a quiet host
HYPOTHESIS-ID: nohangar-route-stall-h1-h3
Precondition: `uptime` load <2. Then `zsh scratch/agent/s5048_preS5038_source.sh`; hangar = H1 (host load), nohangar = H3 (generated code). If load >2, stay BLOCKED; do not run.
