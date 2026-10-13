# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

s4732: port reaches mission VI 512 @0x690400 at 68.3 s on the s4724 schedule (scratch/agent/s4732_run.sh) and sustains it to 150 s; H-route refuted. Mission frame shows terrain as detached ribbons, no ship/HUD.

Work unit: capture retail mission RDP (oracle rdplog, s4724 recipe, gate on VI 512 @0x690400 after initMission) and port mission RDP (s4517_port_rdp.sh adapted to the s4732 key schedule). Per-sync tri/texrect histogram first, then first differing command at the first aligned mission frame (scratch/agent/s4517_diff.py).
Hypotheses: H-stream-equal (streams match, renderer-side defect); H-rsp (geometry/vertex words differ, RSP idiom defect); H-dl (display-list/terrain mesh data differs upstream of RSP).
Discriminator: first differing command + tri count ratio. Positive control: retail vs itself zero diff; hangar vs mission nonzero.
