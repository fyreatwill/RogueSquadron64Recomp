# Next work unit: where do flown-mission triangles vanish between RDP submit and the framebuffer?
HYPOTHESIS-ID: m6-flown-render-fidelity

s5424: flown stream has 2.4M tri (hangar-level per submission) so H1-upstream is rejected. Remaining:
H4 RT64 culls/clips/depth-rejects flown geometry; H3 fb dump captures a partial/early frame; H2 truly empty sky (unlikely).
Discriminator: one run (m6_keyed_hold.sh, already arms TRICOUNT) that also enables the fb dump (see s5421 fbd flag in git show b5f4ced6) at VI phases right after 0x690400 and later, plus RT64 per-frame draw-call/tri count at processDisplayLists. Tri submitted high + RT64 drawn count near zero => H4 (then bisect scissor/depth/viewport); drawn count high + dump empty => H3; both normal => view full-res frames with tools/ppm2png.py. Keep autopilot free of 'r'.
