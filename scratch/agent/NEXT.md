# NEXT: G1 - s5867: find the gate that skips the player-craft update in the frozen window
Context: s5866 [plw] census - in the frozen window no store reaches the player record; updatePlayerCraftPhysics (funcs_30.c:5656) has 10 callers (funcs_28:11574, funcs_31:2761/18652/24276/31674, funcs_32:6478/14292/21122/25780), i.e. per-craft-type update funcs, probably reached via an object-update dispatch. A (0x8000) restarts it.
Hypotheses: H29a the per-object update loop skips the player node via a flag bit (e.g. +0x14 bit) set while landed/idle, A clears it; H29b the craft-type update func returns early on a state word (landed/mode) before calling physics; H29c the dispatcher stops being invoked at all (task/scheduler gate).
Discriminator: one soak with a call counter + entry log of each of the 10 caller functions (and their entry early-return branch) plus the player node's +0x14 flags word dumped 1 Hz alongside [plw]; control: counters fire pre-freeze and after A. Outcome map: caller runs but returns early -> H29b (read its branch condition); callers never run -> H29a/H29c (instrument their dispatcher/caller-of-caller and node flag).
Start with static: which caller handles the player craft (record 0x80137DC0) - check [bit8call] note in CURRENT-TRUTH line ~24.
HYPOTHESIS-ID: g1-mission-progression
Also: backtrace Bus error far=0x3c2d5b616 / 0x37fffd040 (M6) when a run recurs it.
