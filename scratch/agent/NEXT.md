# NEXT: G1d widescreen/ultrawide, first discriminator
HYPOTHESIS-ID: g1d-widescreen
G1c phase 2 closed (s6102, dd capped at 2). Take G1d: find which levers set the 3D aspect. Candidates: H-fov (projection scalar 0x130C50 from s6024), H-viewport (viewport/scissor in the DL), H-fb (framebuffer width), H-hud (HUD x positions). One build, env ROGUESQ_ASPECT=4:3|16:9|21:9 with a per-lever toggle; measure in a fixed-camera framebuffer on level 1 whether the extra width draws (not stretches). Start by grepping CURRENT-TRUTH/PORTING-STATE for 0x130C50 and how RT64 gets its output aspect.
