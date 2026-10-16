# Next work unit: read s5047 verdict (route_flake_hostload) and act on the outcome map
HYPOTHESIS-ID: m3-idiom-class-audit
Hypotheses: H1 host load/key delivery flake (Chrome 118% CPU, load 7.2 observed s5047); H2 s5038-s5040 mq census / lib weak hook; H3 stale build state. s5041/s5042 hooks and save file already refuted (s5046).
Measurement: scratch/agent/soak_results/s5047_route_flake_hostload/keys{1,2}.log (per-key rc, load, hangar/nohangar + last origin).
Outcome map: both hangar => H1, fix recipes (quiet host, longer waits) and resume s5038 mq census; both nohangar with key rc=0 and load high => try after quitting Chrome; both nohangar, load low => build with s5038 census/s5039 hook compiled out (H2), same recipe; key rc!=0 => winctl/trust problem (boring), fix permissions; mixed => flake rate, widen retry loop.
Positive control: winctl key rc logged per press; title origin reached proves the game runs.
