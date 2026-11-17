# NEXT (s7538)
HYPOTHESIS-ID: class-gb-device-done-before-read

s7537 closed class GA as an owner opt-in (ROGUESQ_SP_LATE=1, census exits 0). Read PORTING-STATE s7535-s7537.

Fold first, if SOAK-RESULTS has a new s7536_splate_cost line (it ran on AC): `python3 tools/s7537_ring_cost.py
scratch/s7536_splate_cost l1d1e l1d1l l1d4e l1d4l l4d1e l4d1l l4d4e l4d4l l12d1e l12d1l l12d4e l12d4l --from 72` -> update the
OWNER-OPT-INS SP_LATE row's cost sentence with the AC numbers.

Work unit: class GB, a static idiom-class audit (ITERATION item 3 model). GA was one device telling the guest "done" before
it finished reading guest RAM. Enumerate EVERY completion signal the runtime raises to the guest (grep lib/N64ModernRuntime
ultramodern + librecomp + src/ for the MI/SP/DP/PI/SI/AI/VI interrupt raise / osSendMesg-to-event-queue sites: sp_complete,
dp_complete, pi/si dma done, ai buffer, vi retrace). For each: which guest-RAM bytes does that device still read or write AFTER the
signal (e.g. AI: audio buffer consumed after the AI interrupt? SI: controller block written after si done? RDP: RT64 reading
the DL/texture memory after dp_complete under RDP_ASYNC? VI: origin/fb read after the retrace message?).
Classify each: H-ordered (all access completes before the signal), H-copy (bytes copied before the signal, so later guest writes
are harmless), H-latent-fix (access after the signal with the guest running). Write tools/s7538_gb_census.py in the same style
as tools/s7535_ga_census.py (planted fixture control + mutation control), exit 1 on open H-latent-fix rows.
Hypotheses: H-none (GA was the only one: every other device copies first) vs H-ai / H-rdp-async (a sibling exists).
Any H-latent-fix row gets a same-run alt A/B in the next session (GA_CHK pattern), not a guard.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
