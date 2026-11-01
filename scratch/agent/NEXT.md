# NEXT: G3 -- fix the mission-start load-frame edge lines (follow-mode 3 presents a stale target)
HYPOTHESIS-ID: g3-intro-swap-edge-lines

s6734: during the hangar->mission load the VI shows 0x80690000 (fresh 512x448 flight buffer, all-zero in RDRAM), but
follow-mode 3 (lib/rt64/src/hle/rt64_present_queue.cpp ~L319) presents the last-drawn target 0x62B800 w=640 (faded
hangar) -> thin light edge lines for ~1 s. Retail would show black.
Change (one build, env-gated so both arms run on one binary): in mode 3, if viAddr is NOT within the last-drawn target's
span [drawn, drawn + drawnW*h*bpp) and fbManager.find(viAddr)==nullptr (VI buffer never drawn), do not override: let the
RDRAM path present VI's buffer. Knob ROGUESQ_VI_FOLLOW_STALE=1 (new rule, default) / =0 (old). Must keep the 1024 phase
(VI origin 0x790400 inside drawn 0x790000 span) and every title/hangar/flight screen unchanged.
Arms: scratch/s6734/dense.sh fix43 none "ROGUESQ_LIVES_CAP=1" and ctl43 with ROGUESQ_VI_FOLLOW_STALE=0, run back to back.
Measure: scratch/s6732/dark.py on both capture dirs (fix: dark load frame with bright 0; ctl: the 205/1107-px lines),
plus a 1024-phase / title / hangar / flight window check (captures t=236.. in the recipe cover hangar+load+flight; also
check a boot capture of the attract 1024 phase). lib/ edit -> ./submodule-patches/export.sh + commit same iteration.
Outcomes: fix dark+clean & screens unchanged -> land; lines persist -> the substitution comes from another path (pe gate
forceAdv in rt64_state.cpp ~L3824), trace that; any screen goes black -> rule too broad, narrow by drawnChg/age.
