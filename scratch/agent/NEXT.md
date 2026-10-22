# NEXT (s5904): which collider obj produces cin=1 at a RET event

HYPOTHESIS-ID: g1-mission-progression

s5903 refuted a pointer join obj->candidate node (0/256) and showed one candidate id is paired with 27-71 different collider objs, so r16 is not the owner of the sphere-tested obj. `rs5856_cin` is only an OR flag, so the obj behind an actual hit is still unknown.

Hypotheses:
- H-nested: RET for candidate id X is gated on a hit against a specific obj class (vtable) among the walked list; record (sin_ obj w0) at each RET and a histogram of w0 per id -> a small stable set of vtables for RET ids 52/66/cc/f2.
- H-any: RET fires whenever ANY obj is in-sphere (w0 distribution at RET equals the overall distribution) -> the candidate loop is a broadphase and the objective match happens after RET in the caller.
- H-late: hit objects are irrelevant; the objective check is in the code after the RET (read the caller of intersectSegmentWithObjectSphere statically).

Discriminator: add `rs5856_sinobj` (last obj with sin_=1 this candidate iteration, reset where rs5856_cin is reset) and at `[s5856] RET` print id, sinobj, its w0/w4, and tally w0 over RET events vs over all sin_ events (one table, one build, one run of scratch/agent/s5902_life.sh). Positive control: RET lines fire (15 in s5903). Also dump caller disassembly of the RET path from RecompiledFuncs (static, same iteration).
