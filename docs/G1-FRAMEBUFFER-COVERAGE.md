# Level-0 framebuffer class check

Session 6655, 2026-10-29. Offline scoring with the unchanged
`tools/g1_flight_class.py`; no build, game launch or new capture.

| Image | Dimensions | Sky | Terrain | Craft | HUD | Overall |
| --- | --- | --- | --- | --- | --- | --- |
| [Port oracle-pair crop](g3_port_lvl0_oracle_pair_f5000.png) | 512x358 | pass | pass | pass | pass | pass |
| [Port flight crop](g3_port_lvl0_flight.png) | 512x358 | pass | pass | pass | pass | pass |
| [Saved retail oracle](g3_retail_lvl1_flight_oracle.png) | 512x440 | pass | pass | pass | pass | pass |

Both port files have the same decoded RGB SHA-256:
`3f7061b7752672aee0d81d9025c157cb871ba0ae7f2738bdd8a9451ee78abddd`.
They are one image witness, not two independent captures. Both score relative
terrain energy 0.115, chase-band metal 0.119, radar fraction 0.095,
sky luma 179.2 and R-minus-G -70.3. Craft passes via metal >=0.10;
terrain passes the original [0.08,0.33] band, not the snow arm.
The crop removes lower-screen content but retains every required feature
inside its normalized classifier window. No clause fails.

Visual inspection shows a banked X-wing, sandy terrain at lower right,
blue sky, green reticle, top-left wingman icon and top-right radar. The
retail image shows the same content classes with a different camera pose
and a lives badge near the bottom. That badge is not required by the
four-clause rule. This supports content presence, not pixel equivalence.

The complete classifier control table reports `canon_bad 0`, including
positive flight images and negative title, floor, craft-select, crest
and pause images. The level-3 set remains `mission 11/13`. The retail
oracle's terrain energy is 0.129, metal 0.156 and radar 0.088.

Provenance limits: s5985 calls the retail comparison a different level;
s5998 calls it a same-level pair. The filename says `lvl1`, while the port
route is recorded as level 0. This check establishes neither retail level
identity nor a matched camera. Earlier entries call the retail height 412;
the saved file decoded here is 440 pixels high. Use measured dimensions.
Visual inspection and numeric scoring agree on the content classes, but
both describe these saved images. No new independent runtime observation,
objective response or endurance result is claimed.

Reproduce from the repository root:

```sh
python3 tools/g1_flight_class.py
python3 tools/g1_flight_class.py docs/g3_port_lvl0_oracle_pair_f5000.png docs/g3_port_lvl0_flight.png docs/g3_retail_lvl1_flight_oracle.png
```
