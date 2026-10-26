# G1d: stop the wide-title writeback from dumping undrawn native-target rows
HYPOTHESIS-ID: g1d-widescreen
s6244: ph4 colour writeback (addr 0xB3B200, ww=900, rows 0-447) covers the whole VI scan-out (origin 0xB3AE00, w=512 h=444). Noise below y~255 = RT64 native-target content for undrawn rows.
Hypotheses: H-uncleared (native target rows never drawn hold garbage -> clear to black on fb alloc/resize, or clamp writeback rows to the drawn extent); H-vi-width (VI should read w=900, mismatched stride is the real bug).
Discriminator, one build: in the wide route (s6244_run.sh) add env ROGUESQ_WB_CLAMP_ROWS=<n> (cap cRowEnd for ww=900 ph4) and ROGUESQ_WB_CLEAR=1 (zero the native target at resize); compare fb_0001000 non-black fraction below y=255 in one run per arm; control = unmodified arm still noisy.
