# NEXT: G1c - implement ROGUESQ_DRAW_DISTANCE on 0x8009DEAC and fold [gridlog] arms
HYPOTHESIS-ID: g1c-draw-distance
Facts (s6035 code read): polygon unclamped; knob = float at 0x8009DEAC (14.5), DEB0 recomputed each call; limits = terrain w/h + 64-wide window bitmaps (overflow risk if window >64).
H-A: DEAC scaling widens the window until terrain/64 stride saturates. H-B: earlier x2/x3 arms never scaled DEAC (explains +4%). Discriminator: fixup script writes DEAC*=ROGUESQ_DRAW_DISTANCE (clamp so window<=64, never change default), run lvl1 at 1.0 vs 2.0 with ROGUESQ_DD_GRIDLOG=1 in one build; compare win w/d and kept. First fold the queued s6034_g1c_ret/posab [gridlog] output from SOAK-RESULTS.
