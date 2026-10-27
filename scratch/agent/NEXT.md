# NEXT: what does the span-grid consumer do with saturated bytes (0x80/0x7F) at cols>=32?
HYPOTHESIS-ID: g1c-span-reject-predicate

s6522: clamp bounds are the fixed signed-byte range (127/-128) in both arms; inputs finite and equal between arms; dd4 pre-clamp values at col>=32 reach -472/344, so 0x80 is a legit saturation (H-clamp-legit selected; bound-swap and input-bad refuted).
Hypotheses: H-reject-by-design (consumer compares span bytes and rejects saturated cells; retail never reaches col>=32 so it is only a dd>1 artefact), H-scale (dd>1 needs the f22=40 scale / row slope rescaled so values stay in byte range), H-consumer-bug (compare treats -128 incorrectly, e.g. unsigned lb vs lbu).
Discriminator: locate the consumer load of the grid bytes (lb vs lbu, compare against what) in streamTerrainGridCellsByDistance; log per accept/reject decision at col>=32 for dd4 with the byte value; then an arm that forces f22 /= (dd) to keep values in range and counts EMPTY cells (positive control: dd1 unchanged). If EMPTY drops => H-scale.
