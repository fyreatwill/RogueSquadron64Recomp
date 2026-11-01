# NEXT: G3 -- the mission-load right-edge vertical line (stale presenter column after a full-width -> 4:3 change)
HYPOTHESIS-ID: g3-load-edge-column

s6735 fixed the horizontal load line (follow-mode 3 stale target, ROGUESQ_VI_FOLLOW_STALE). The vertical line remains in
every arm: window x=1278 (W-2), y 410..818, during the ~1 s dark load. In hangar captures the window is drawn edge to edge
(column W-2 lit); in the load frames only that column stays lit while everything else is black.
Hypotheses: H-clear (RT64's presenter clears/draws the pillar bars with a rect that stops 1-2 px short of the right edge,
so the old hangar pixels survive there); H-scale (the 4:3 content rect is computed with rounding that leaves the last
column untouched by both the content and the bar fill); H-src (the presented source texture has a lit last column).
Discriminator, one build: in the present path log the swapchain size, the content rect (x0,x1) and the clear/bar rects on
the load swaps; plus scratch/s6735/dense.sh with captures. H-src would show the column inside the content rect (it is
outside: content x 86..1192), so expect H-clear/H-scale. Fix = clear the whole swapchain before drawing the content rect
(or extend the bar rect to W). Arms: fix vs knob-off on one binary; scorer scratch/s6732/dark.py (vertical 205 px -> 0)
plus boot scorer scratch/s6735/boot.py. lib/ edit -> export.sh + commit.
