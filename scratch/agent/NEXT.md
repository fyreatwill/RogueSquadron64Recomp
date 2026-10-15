# Next work unit
HYPOTHESIS-ID: m5-audio-destub-sequence
s4966 closed the mission image-vs-silent A/B (H-stable-both, crash=0 both arms). Unit: pick the next unqualified step in docs/M5-AUDIO-PLAN.md execution table (Step 10 host PCM consumer, or a >=600 s mission hold with the image arm; copy scratch/agent/soak_queue/done/s4964_mission_image_*.sh with longer timeouts and enqueue). Record the plan row first, then enqueue; do not babysit.
Outcomes: crash/stall in a long image hold => name the writer (rule 11); clean => mark the step qualified in the M5 plan.
