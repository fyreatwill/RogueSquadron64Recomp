# Next: re-baseline the nohangar route stall (tree restored in s5050; cmake --build is safe again)
HYPOTHESIS-ID: m3-idiom-class-audit
Order: (1) rebuild from the restored tree and check whether nohangar stalls as before; source now equals the ea2e382f-era code, so H3 (build state) is testable again. (2) With Chrome/REAPER quit if possible, run scratch/agent/s5048_preS5038_source.sh as the host-load check (H1). (3) Quiet host + stall => property of generated code (H3).
Never run tools/agent/regen_n64recomp.sh or regen in place.
