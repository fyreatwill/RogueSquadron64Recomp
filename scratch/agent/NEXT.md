# Next work unit
Fold soak s5486_menu_fb_dump (scratch/agent/m6/s5486_menu_fb/fbd/fb_*_w*.ppm, ppm2png.py in scratch/agent/m6/). Positive control: in-mission frames (w512) look right. Then inspect post-phase-6 frames (w640/1024) for garbling/missing text/wrong palette; if 32bpp VI mode shows noise, add bpp handling from VI_STATUS_REG. Do NOT use autopilot 'r'.
HYPOTHESIS-ID: menu-overlay-fidelity
