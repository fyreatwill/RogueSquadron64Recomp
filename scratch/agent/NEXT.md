# NEXT: lift the dd>3 cap and produce a dd1-vs-dd4 owner contact sheet
HYPOTHESIS-ID: g1c-dd-phase2
State (s6581): true dd4 (DD_UNSAFE=1) 300 s clean on lvl1/5/10.
Work unit: edit tools/apply_s6036_dd.py:7 so dd up to 4 is allowed without ROGUESQ_DD_UNSAFE (keep 8 under UNSAFE; default stays retail 1.0). Regen order: apply fixup -> cmake (DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer). Verify log prints "multiplier 4" without DD_UNSAFE. Then same-pose framebuffer contact sheet dd1 vs dd4 (reuse docs/owner_sheet_s6546 recipe) for the owner.
Outcomes: multiplier 4 w/o UNSAFE + sheet => close cap item; still "capped to 3" => the fixup did not re-apply, check regen order.
