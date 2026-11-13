# NEXT (s7289): fold s7290_window_depth — what removes the dd>=5 window's extra forward rows?
HYPOTHESIS-ID: g1c-window-bind
State (s7288): dd>=4 window = 128 side x cap/128 deep (cap 2048*ceil(dd), px clamp 5): 128x64 dd4, 128x80 dd6, yet cells/call
3490 -> 3552 (+1.8% for +25% area). Ctl WIDEWIN=0 pins 64x64 (instrument PASS).
Unit: fold scratch/agent/soak_queue/s7290_window_depth.sh (L4 16:9 dd6 ref / OFFMAPCULL=-1 / POOLX_MAX=8 / both). If voided or
still queued, run it in-session: `zsh scratch/agent/soak_queue/s7290_window_depth.sh` (~11 min, idle host, AC).
Outcomes (cells/call vs ref 3552; depth from tools/s7289_window_bind.py):
  - H-offmap: nocull grows cells (px8nc most) -> the K0.6 off-map cull eats the depth; retune K with a look check (s7034-s7036 image).
  - H-cap-only: px8 alone grows cells -> raise the px clamp in the dd bundle, measure cost (win77-97 must stay 60/s).
  - H-far: no arm grows -> the stream's far clip/fog end cuts it; find that constant (L-radius in the G1c list) next.
Positive control: px8 must report depth 96 (cap 12288 /128) in the site-17 trace, else the arm did not take.
