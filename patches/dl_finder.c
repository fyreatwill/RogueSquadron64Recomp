// s6278 C-patch #3: multi-call stateful. Re-implements findAndUnlinkSmallestEntry
// (0x8002221C, display-list chunk finder). Despite the name the retail loop keeps the
// LARGEST non-empty entry (replaces on size >= best, ties go to the later node); ported
// verbatim. Picks it out of the bucket lists at [0x80128F00], unlinks it, pushes it on
// the list headed at [0x80128EF8], returns its word at +0x14. Returns 0 when every
// bucket is empty (the dd>=3 exhaustion signature). fixup_patches_host.py wraps the
// generated body with an env-gated NULL-return pool dump and an invariant check.
typedef unsigned int uint32_t;
typedef unsigned short uint16_t;

#define RECOMP_PATCH __attribute__((section(".recomp_patch")))

typedef struct Entry {
    struct Entry* next;   // 0x00
    struct Entry* prev;   // 0x04
    uint16_t size;        // 0x08
    uint16_t bucket;      // 0x0A
    uint32_t pad0c[2];    // 0x0C
    uint32_t payload;     // 0x14
} Entry;

extern volatile uint16_t dl_bucket_count;   // 0x80128EF0
extern Entry* volatile dl_used_head;        // 0x80128EF8
extern Entry** volatile dl_buckets;         // 0x80128F00

RECOMP_PATCH uint32_t findAndUnlinkSmallestEntry(void) {
    uint32_t count = dl_bucket_count;
    Entry** buckets = dl_buckets;
    Entry* best = 0;
    uint32_t i;
    if (count != 0) {
        for (i = 0; i < count; i++) {
            Entry* n;
            for (n = buckets[i]; n != 0; n = n->next) {
                uint16_t sz = n->size;
                if (sz == 0) continue;
                if (best == 0 || !(sz < best->size)) best = n;
            }
        }
    }
    if (best == 0) return 0;
    {
        Entry* next = best->next;
        if (best->prev != 0) best->prev->next = next;
        else dl_buckets[best->bucket] = next;
        if (next != 0) next->prev = best->prev;
        {
            Entry* head = dl_used_head;
            best->prev = 0;
            best->next = head;
            if (head != 0) head->prev = best;
        }
        dl_used_head = best;
        return best->payload;
    }
}
