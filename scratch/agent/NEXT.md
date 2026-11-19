# NEXT (s7614)
HYPOTHESIS-ID: host-static-aggregate-pointer-member

Class HP closed s7613 (tools/s7613_hp_census.py --controls: 65 pointer-typed static-storage variables, regex census ==
clang-AST census, 4 guest views gated/fresh/log-only, contracts B/B1/B2/F1/H1, controls 9/9, H-clean). Its declared scope gap
is the next class.
Class HM: pointer MEMBERS of static aggregates - a static / thread_local / file-scope variable of record type (struct
instance, std::array / C array of structs, vector/map/deque<Struct>, std::function / lambda closure) whose record has a pointer
field (T*, atomic<T*>, iterator, std::function) holding a host view into guest RAM (TO_PTR / rdram + off / OSThread* /
OSMesgQueue*) that is dereferenced on a later call.
Method: extend tools/s7613_hp_ast.py (it already parses every VarDecl with static storage): also collect CXXRecordDecl /
RecordDecl FieldDecls, then emit every static VarDecl whose (element) type names a record with a pointer field (recurse one
level into nested records; std:: templates: take the template argument record). -> tools/s7614_hm_ast.py. Regex side: for each
record with a pointer field, grep `<record>` static declarations (tools/s7614_hm_scan.py), and an HP-token member-store scan
(`x.field = TO_PTR(...)`, `x[i].field = rdram + ...`, `->field = TO_PTR`) restricted to records in the list.
tools/s7614_hm_census.py: rows (file, var, field) -> base / host / gated / fresh / logonly / keyed / event / BAD, with proof regexes.
Hypotheses: H-clean, H-bad-gated, H-bad-live.
Controls: (1) plant a static struct with an OSMesgQueue* field set from TO_PTR and read in a later call -> OPEN; (2) drop a
row -> OPEN; (3) plant a static std::vector<S> where S has a T* field -> listed by both censuses; (4) drop one record from the
regex side -> AST disagreement OPEN.
Second source: the clang AST census (as s7613); if any default-on guest view is found, a runtime witness from an existing log.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
