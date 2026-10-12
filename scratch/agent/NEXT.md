# NEXT: renderer-side triage of hangar artifacts (RT64 tri-index mask)
HYPOTHESIS-ID: hangar-renderer-artifacts

RESUME: s4634 closed the M4 RSP/stream thread: port hangar entry RDP stream equals retail
except 3 animating tris. Visible rim band / blue holo spikes / right-edge garbage are
renderer-side.
Hypotheses: H-tri (specific tris, e.g. range 850-1246, render wrong in RT64), H-state
(an RDP state/combiner/texture-format path RT64 mishandles), H-fb (framebuffer/VI side).
Discriminator: env-driven tri-index mask in the RT64 tri submit path (single run, bisect
index ranges); hide ranges and see which removes the artifact. Positive control: masking
all tris blanks the frame. Capture screenshots per mask. Any lib/ edit needs
submodule-patches/export.sh + commit.
