# NEXT (s7217): G3 21:9 remaining screens (MISSION FAILED, level description, chapter crawl, PAUSED) vs angrylion
HYPOTHESIS-ID: g3-21x9-remaining-screens
Context: s7216 closed the 21:9 long-route front end (GAME OVER/results, wipe, ER, SELECT GAME/LEVEL, AVAILABLE CRAFT, hangar) as H-match
once the scorer used the RT64 row model (FID_ALROWS=444 for 448-row fbs, 336 for 339-row fbs). Not reached at 21:9: MISSION FAILED (that
run showed GAME OVER), the level-description overlay, a chapter crawl (640-wide fb, 640x300) and PAUSED over flight.
Hypotheses: H-match (centre band at the 4:3 floors of s7181/s7183/s7184, undrawn sides black); H-shift (the 640-wide crawl fb or the
pause overlay placed/scaled differently in the 21:9 box: dx != 0 or a band-local dy in scratch/s7216/yprof.py); H-rows (the crawl's
300-row band shows a row count other than the model, giving a linear dy drift that FID_ALROWS must absorb - itself a datum).
Discriminator, 1-2 runs, one at a time:
 A. crawl + pause: the s7183 B route at 21:9: env RDIR=s7217 ASP=21:9 AP=<s6995 route to 64:a>,262:start SECS=300 FROM=2300 EVERY=12
    DL=66 DU=234 CW=1680 CH=720 zsh tools/s7146_arm.zsh B1 "" (owner recipe FPS60 dd4; check s7146_arm's ASP handling first).
 B. level description: AVAILABLE CRAFT + C-up (s7184 route), 21:9.
 Post tools/s7152_post.zsh, then per screen: yprof (dy flat?), FID_ALROWS chosen by the yprof test (444/336/other), tools/s7122_fidelity.py
 score + --shift 2 + a +4-row rect (registration control must fire). Crawl uses FID_MAINRUN=1 if its fb paints stray rows.
Each outcome names its hypothesis; fix H-shift in the same iteration. MISSION FAILED: the forced-L17 route shows it on some runs
(s7173: ~125.9 s); if this run shows GAME OVER again, note it and do not chase it.
