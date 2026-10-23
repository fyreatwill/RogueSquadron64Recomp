# NEXT: fold s6006_hangar_route_{a,b,c} (G3/G4)
HYPOTHESIS-ID: g4-crash-stall-hunt
G4 closed 0-18 (s6006). Fold the three hangar-route soaks from SOAK-RESULTS.md (grep crashlines/vi_stalls30s). Any abort/stall -> lldb or ASan backtrace, name the writer, root-cause. All clean -> record hangar-route failure rate (previously ~1/3-3/5 launches) and take G5 renaming sweep or parked hangar artifact with a new angle.
