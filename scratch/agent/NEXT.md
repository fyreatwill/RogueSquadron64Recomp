# Next work unit: design a new M4 shared-boundary discriminator
HYPOTHESIS-ID: m4-shared-boundary-revisit

Do one offline design/measurement pass for the parked M4 accumulator thread.
The previous comparison joined retail cxd4 samples to port phase records but
used different RSP-PC domains and different phase origins. Build no runtime
instrument until the independent oracle boundary and the port boundary are
defined in the same task-key domain.

Competing hypotheses:

* H1: a shared task-keyed boundary can join retail and port samples, and the
  transient `0x8000` lane is the same legitimate accumulator behavior.
* H2: a shared boundary joins, but the lane differs between implementations;
  a writer/origin investigation is then justified.
* H3: the remaining key-domain mismatch is structural, so this boundary is
  unevaluable and the thread must remain parked.

Discriminator: write down the exact retail task serial, RSP-PC/step bucket,
VI origin, and port task serial/PC/step fields that must join for one 512-wide
hangar task. The result must specify what concrete row would select H1 or H2;
an absent join selects H3. Consult `docs/REVISIT-S5325-M4-SHARED-BOUNDARY-DESIGN.md`
and the oracle README before building anything.
