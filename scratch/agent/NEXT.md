# Next: restore N64Recomp/RecompiledFuncs (see BLOCKED.md), then re-baseline the nohangar route
HYPOTHESIS-ID: m3-idiom-class-audit
Order: (1) human restores tree from backup; (2) with Chrome/REAPER quit, run scratch/agent/s5048_preS5038_source.sh (host-load discriminator H1) using the surviving build/ binary; (3) if still nohangar with a quiet host, the stall is a property of the current generated code (H3), not host.
Never run tools/agent/regen_n64recomp.sh (now disabled) or regen in place.
