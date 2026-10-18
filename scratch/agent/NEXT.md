# Next work unit: locate the mission-failure swap and explain the recurring MISSION GOALS overlay
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5430): 310 s hold (swaps 0-7470, dumps every 10) shows no failure text; goals overlay appears 3x. s5429 saw MISSION FAILED by VI ~12000.
Hypotheses: (A) overlay is periodic HUD (goals reminder); (B) mission restarts (retry path from autopilot 'start'/'z' keys); (C) ship destroyed later with no input.
Discriminator: `env FBD_EVERY=20 zsh scratch/agent/m6_keyed_hold.sh s5431a 560`, then contact sheet of every 20th dump (PIL via plain python3, NOT -I), find first failure frame and compare the overlay frames' preceding frame (menu/title = restart; flight = HUD). Positive control: the goals overlay frames already seen. Delete dumps afterwards (~1 GB, gitignored). Then add flight keys so the ship survives.
