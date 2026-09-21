# M5 s3677 — task-keyed source/stage join

The first implementation keyed image-stage rows only by `task_data_ptr`. The
qualified 55-second run showed that this pointer is reused: stage route
ordinal 1179 matched an older source record at ordinal 656. That result was
discarded and the instrument was fixed to require task pointer, route ordinal,
and route row for an exact match, with separate same-pointer/different-route
and prior-different-task fallbacks.

The corrected concurrent run passed the oracle whole-RDRAM, descriptor, title,
hangar, and type-2 controls, plus the port source-hook, source, phase, ABI,
and stage controls. It recorded 1,024 source rows (512 title and 512 hangar),
1,922 stage rows, and 1,942 stage joins. The join classes were:

- `source_match=1` exact task-pointer/route match: 0
- `source_match=2` same task pointer but earlier/different route record: 1,972
- `source_match=3` prior record from a different task pointer: 2
- no source record: 8

Normal rows commonly differed by one route ordinal (stage 2 versus source 1)
with age 2–4 join events. Sparse rows retained much older same-pointer records;
for example title stage ordinals 460 and 463 used source ordinal 91 with ages
6,706 and 6,736, and hangar ordinal 464 behaved similarly. This refutes an
exact route/task join for the current callback path and shows that pointer-only
matching is invalid. It supports route/callback timing as the leading
explanation, but cannot distinguish cross-thread timing from publication lag.

The independent oracle run reached title and hangar and recorded 343,272
whole-RDRAM writes, 674 source-span writes, 905 type-2 task rows, and all four
descriptor watch controls. It does not expose the port's internal task key, so
the source/stage classification remains single-source port evidence.
