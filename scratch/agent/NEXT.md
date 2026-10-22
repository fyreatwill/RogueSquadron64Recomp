# NEXT (s5910): find who POSTS NPC message type 5 (damage) and what gates it per bolt

HYPOTHESIS-ID: g1-mission-progression

s5909: findSegmentObjectSphereHit callers are not damage (occlusion/LOS/lock-on). Damage is msg5 reaching npcProbeDriod via a queue (host stack has no sender, ra=0).

Hypotheses:
- H-post-gate: a bolt-update function posts msg5 only when a predicate (team/owner/range) passes; 12 ids never get it.
- H-other-prim: the bolt uses a primitive other than 0x8006A944 (e.g. inline segment/sphere or findNpcInScaledBoxRegion/AlongDirectionRay: 8005eb5c 7806 calls/0 hits is the box-region caller).
- H-queue-drop: msg5 posted but dropped before dispatch.

Discriminator: (1) static: in N64Recomp/RecompiledFuncs grep for the message-post function (callee of which npcProbeDriod drains) and sites setting a1/msg type 5; name the poster functions. (2) one run tallying calls/args per poster per bolt id, with control = posters for msg3/4 firing (s5893 had msg3/4 per-id control).
