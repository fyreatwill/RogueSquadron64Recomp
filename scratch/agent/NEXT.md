# NEXT: right-edge hangar garbage is FB/VI-side — locate which layer
HYPOTHESIS-ID: hangar-renderer-artifacts

RESUME: s4635 showed right-edge garbage (x>=1276 of 1280 screenshot) is bimodal across
identical runs and persists with every triangle masked (ROGUESQ_TRI_MASK=0-99999999).
Hypotheses: H-rdram (columns >=~510 of the 512-wide colour image at 0x006AB400 are garbage
in RDRAM: fill/copy/texrect writer), H-rt64-fb (RDRAM clean; RT64 FB readback/VI scale/crop
reads past width), H-vi (VI h-start/x-scale makes the last column sample beyond the image).
Discriminator: same run, dump RDRAM colour image columns 504-511 (rows 0-239) at hangar phase
AND the screenshot edge; run until at least one bimodal garbage-present run and one absent run
(compare same-config reruns). RDRAM garbage present+screenshot garbage => H-rdram (then find
writer with the oracle/retail comparison); RDRAM clean+screenshot garbage => H-rt64-fb/H-vi.
Positive control: ROGUESQ_TRI_MASK=0-99999999 still blanks geometry (verified s4635).
Tools: scratch/agent/s4635_mask.sh TAG [ENV=..], s4635_strip.py.
