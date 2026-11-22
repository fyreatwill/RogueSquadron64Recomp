# NEXT (s7803)
HYPOTHESIS-ID: retained-input-gate-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c holds are 19/19 (s7802); G6c waits on the owner only.

Unit: the sweep's 3 REPORT rows (s7031_offmap_census, s7210_field_census, s7441_rs64_census; tools/s7651_gate_sweep.py REPORT dict)
say "input not retained" / "no open class". s7802 found two gates whose "absent" inputs were really *.zst. For each REPORT row:
(1) find its source capture (grep PORTING-STATE for the session, then `ls scratch/s7030 scratch/s7210* scratch/s7442`, incl. *.zst);
(2) if retained, decide if the summary has a checkable claim (a number the ledger pinned) and a plantable control: then make it a
gate (S7723_RETAINED-style row + a planted RED in tools/s7723_retained_controls.py or a --controls flag) and read it through
tools/rs64_zopen.py; (3) if not retained or no claim, leave REPORT but correct the note with what was checked.
Hypotheses: H-retained (>=1 input exists, maybe as .zst -> new gate), H-gone (all absent -> notes corrected, class closed),
H-claimless (inputs exist but the tool only prints tables: REPORT is right).
Then the 6 one-off analysis scripts s7802 listed (g1_flight_class, g1d_levelselect_tear, g3_cine_tri, g3_rdp_top_envelope,
g5h_band_pose, pd2_corr) open now-.zst inputs raw: switch them to rs64_zopen only if one is cited as evidence in CURRENT-TRUTH.
