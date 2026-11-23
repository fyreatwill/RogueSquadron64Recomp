# NEXT (s7864)
HYPOTHESIS-ID: g3-ai-vi-clock
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7863): g3-audio-clock-sign CLOSED as timing class. AI buffers are a fixed 0x300 (code constant); one song-end buffer count
N fits both arms in all 10 song windows (`python3 tools/s7863_song_end_threshold.py --control`, sweep row S7863_SONGN). The port's
AI-done messages are host-paced (lib/N64ModernRuntime/ultramodern/src/events.cpp: AI Drain thread, ROGUESQ_AI_EVENT_DRAIN default
2048 B, s4450/s5672/s6790/s7197), so it delivers 0-3 AI buffers per VI vs retail's steady 1-2 and crosses N one VI early.
Unit (bounded change, determinism opt-in like VI_STAMP / RETAIL_SNAP; default unchanged): ROGUESQ_AI_VI_CLOCK=1 posts OS_EVENT_AI
from vi_thread_func with a fractional accumulator: acc += get_audio_frequency() / VI_rate / 192 per VI (0x300 B = 192 stereo
frames; retail measured 1.9146 buffers/VI), post floor(acc) messages, acc -= posted; the drain/HZ threads stay off when it is set
(make ai_event_external() false and branch at events.cpp ~1057). Host audio may under/overrun slightly: determinism harness only.
lib/ edit -> `./submodule-patches/export.sh` + commit in the same session. Rebuild (DEVELOPER_DIR=... cmake --build build).
Then rerun the bonus 17 det pair with ROGUESQ_AI_VI_CLOCK=1 added to the port arms (s7861 recipe, CURRENT-TRUTH item 12; reuse
scratch/s7861/v17 r1 + pins, port arms only) and score with tools/s7856_det_verdict.py + s7863_song_end_threshold.py.
Hypotheses / outcomes:
- H-phase: song 03 ends t1124 on both -> b17 H-exact; then rerun 0x31=14 (shortest other fork) for the second line.
- H-pattern: still splits because mupen CPO1's 1/2 pattern has a different phase than the accumulator (per-VI cum diff
  still nonzero at the crossing) -> seed acc from retail's first AI-buffer VI, or close as harness-only.
- H-other: the per-VI cum diff is 0 everywhere yet the tick still splits -> the end is not buffer-count driven (s7863 model wrong).
Positive control: per-VI buffers histogram for the port arm must become {1,2} only (was 0..3), same-run p2 without the flag keeps 0..3.
