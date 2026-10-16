# Next work unit: fold s5045 control rerun of s5037 on the current binary
HYPOTHESIS-ID: m3-idiom-class-audit
s5044 no-census arms both stalled nohangar (s3290-stall phase 7); recipe identical to working s5037 apart from name/print. Queued s5045_control_rerun_s5037.sh (verbatim s5037 default).
Outcomes: hangar~t=91 + mission onset~174 => binary fine; route is flaky -> rerun poison arms (s5042 recipes) twice, need poison total line as positive control.
nohangar => current binary regressed with poison hook compiled in even when off -> diff s5042 build change, rebuild without hook, rerun control.
