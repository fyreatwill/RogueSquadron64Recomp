# NEXT: G1d close-out — remaining wide-aspect menu screens + owner contact sheet
HYPOTHESIS-ID: g1d-menu-sweep

s6730 fixed the game-over entry sliver (s6158 radar-region shift outliving flight; gate now epoch-scoped).
Remaining unvisited: Elite Rogues and Select Game screens after game over (pillarbox look at 16:9/21:9), then a contact
sheet of every menu (title, main menu, options, passcodes, level select, mission intro, pause, debrief, game over,
Elite Rogues, Select Game) at 4:3 / 16:9 / 21:9 for the owner.
Hypotheses per screen: H-ok (correct pillarbox/centre), H-anchor (s6156 HUD anchor / s6158 region shift misplaces items
-- now epoch-gated, so check items that appear inside flight's epoch), H-pillar (stale RDRAM in pillars, crop not latched).
Command: zsh scratch/s6730/gameover.sh <tag> <16:9|21:9|none> "ROGUESQ_FB_DUMP_EPOCH=<e> ROGUESQ_FB_DUMP_VI=1"
(window captures t=100..200 in scratch/s6730/<tag>/w*.png; epochs 27 = game over, 28 = next screen). Extend AP_OVERRIDE
keys past t=180 to page through Elite Rogues -> Select Game. Discriminator per screen: window capture at each aspect vs
4:3; any misplaced/undrawn item -> grep [region-gate]/[hudc] and RT64 [rtrdp] (ROGUESQ_LOG_RTPAIR_EPOCH=<e>) to see
whether RT64 received the rect where the bridge logged it.
Then: owner contact sheet, then G3 render fidelity.
