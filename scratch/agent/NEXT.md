# NEXT: is desc+4 (0x80136DC4) ever non-NULL on lvl7? (H-retail-null vs H-unbuilt)
HYPOTHESIS-ID: g1c-dd-phase2
State (s6589): window x0=0 w=64 z0=31 d=65 inside grid 93x96 -> overrun refuted. desc w0=w4=0 at fault.
Work unit: log desc+0/+4 each frame transition on lvl7 at dd1 (retail) and at dd4 CAPX=2, plus a write-watch hook on 0x80136DC4. Outcomes: retail also NULL with idx!=0 cells -> retail never indexes record table for these cells (CAPX reaches cells whose flag bits retail skips): inspect cell flag bits (cellh 0x8001) in the visit gate. Retail non-NULL -> our dd4 path runs before the table is built/was freed: find the writer.
