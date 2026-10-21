# NEXT: fold s5745_crawlshot (queued; window screencapture every 6 s on the s5723 intro route)
Read tail of scratch/agent/SOAK-RESULTS.md, scratch/agent/m6/s5745_crawlshot/{shots/*.png,summary,run.log}.
Hypotheses: (H1) bottom-third garbage band is on the REAL window => RT64 colour-image/writeback or fill defect in the 640-wide cinematic; (H2) shots clean => fbd-only RDRAM artifact (unwritten rows in letterbox), retire G3 crawl item; (H3) shots black/missing => capture failed (screen locked/window absent) - void.
Discriminator: view 3-4 shots taken while run.log shows vi_width=640 origin 0x62BD00. Control: >=1 png and a w640 phase row.
THEN (mandatory pivot, iteration MUST commit a build/runtime change): if H1, find the SetColorImage/FillRect for the rows 300-448 and fix in lib/rt64 (export.sh + commit); if H2, land an M3/route change (do not run another observation).
HYPOTHESIS-ID: g3-crawl-band
