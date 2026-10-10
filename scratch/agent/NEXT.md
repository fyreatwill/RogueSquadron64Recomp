# NEXT: M5 audio de-stub (docs/M5-AUDIO-PLAN.md)
HYPOTHESIS-ID: m5-audio-destub
s4553: the +5436 crash persists with ROGUESQ_AUDIO_UCODE=0 (3/3 arms crash), so it is not an audio-image artifact; do not re-run.
Open oddity: the ROGUESQ_DRAIN_INLOOP_TICK=1 arm never left VI 640 in 150 s (early route). Candidate unit: phase-gated repeat (tick-on vs default plus a repeat) to see whether tick-on stalls deterministically.
Alternative: M3 idiom-class audit of the list-walk load pattern in musyxSynthFrame (grep-enumerate all sites, classify).
