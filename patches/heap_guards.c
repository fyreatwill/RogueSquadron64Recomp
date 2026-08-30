// Override of func_80007D74 (heap free-list dequeue + queue insertion) with
// KSEG0 pointer-validation guards added. The originals were inline edits
// in funcs_3.c at L_80007DE0 and L_80007E30; moving them here so the
// auto-generated funcs_*.c can be regenerated cleanly.
//
// The function pops a block off a doubly-linked free list (allocating a
// new chunk via func_8002221C if the list is empty), then inserts the
// popped block into a per-frame "active" queue and bumps the queue's
// allocation pointer. Returns block + 8 (skipping the 8-byte header).

// Standard MIPS gcc with -nostdinc — no system headers. Inline what we need.
typedef unsigned char       uint8_t;
typedef unsigned int        uint32_t;
typedef unsigned long       uintptr_t;  // mips32 ABI: long is 32-bit
#define NULL                ((void*)0)

#define RECOMP_PATCH __attribute__((section(".recomp_patch")))

// 8-byte block header (next, prev). The full block is 0x100 bytes; only the
// first 8 are well-defined here (rest is opaque payload to the allocator).
typedef struct Block {
    struct Block* next;  // offset 0
    struct Block* prev;  // offset 4
} Block;

// Game-side allocator helper (resolved via syms.ld → 0x8002221C).
extern Block* func_8002221C(void);

// Game-side globals (declared in syms.ld at their RAM addresses):
extern Block*  heap_free_head;       // 0x801163B0 — head of free list
extern Block** heap_other_listhead;  // 0x801163FC — pointer to a Block* slot
extern Block** heap_tail_loc;        // 0x8011A7DC — pointer to current tail node
extern void*   heap_bump;            // 0x801163D4 — bump pointer (block + 0x100)

static int kseg0_ok(const void* p) {
    uintptr_t addr = (uintptr_t)p;
    return addr >= 0x80000000U && addr < 0x80800000U;
}

RECOMP_PATCH Block* func_80007D74(void) {
    Block* head = heap_free_head;

    // If the free list is empty, allocate a new chunk (which itself is a
    // chain of free blocks linked via .next) and prepend it to the list.
    if (head == NULL) {
        Block* fresh = func_8002221C();
        if (fresh != NULL) {
            if (!kseg0_ok(fresh)) {
                return NULL;
            }
            // Walk fresh's chain to find its tail
            Block* tail = fresh;
            while (tail->next != NULL) {
                if (!kseg0_ok(tail->next)) {
                    return NULL;
                }
                tail = tail->next;
            }
            // Splice old head onto the end of fresh's chain
            Block* old_head = heap_free_head;
            if (old_head == NULL) {
                tail->next = NULL;
            } else {
                if (!kseg0_ok(old_head)) {
                    return NULL;
                }
                tail->next = old_head;
                old_head->prev = tail;
            }
            heap_free_head = fresh;
            fresh->prev = NULL;
        }
    }

    // Re-read head (may have just been replaced by `fresh` above)
    head = heap_free_head;

    // If head isn't a valid KSEG0 pointer, treat the list as empty rather
    // than dereferencing into garbage.
    Block* new_head;
    if (!kseg0_ok(head)) {
        new_head = NULL;
    } else {
        new_head = head->next;
    }
    heap_free_head = new_head;
    if (kseg0_ok(new_head)) {
        new_head->prev = NULL;
    } else {
        // Keep an invalid published successor from surviving into the next
        // allocation attempt.
        heap_free_head = NULL;
    }

    // The block we'll return is the one we just popped. In the original
    // assembly $r3 (= old head, captured at L_80007DD8) is what flows into
    // $r4 (a0) at the L_80007DFC branch. So `popped` = old head value
    // before we advanced the list above.
    Block* popped = head;

    if (!kseg0_ok(popped)) {
        return NULL;
    }

    // Insert popped into the active queue only after validating the value
    // published by the free-list head.
    if (!kseg0_ok(heap_other_listhead) || !kseg0_ok(heap_tail_loc)) {
        return NULL;
    }
    Block* tail = *heap_tail_loc;
    if (!kseg0_ok(tail)) {
        return NULL;
    }

    if (*heap_other_listhead != NULL) {
        // Queue non-empty — append after current node.
        if (!kseg0_ok(tail->next)) {
            return NULL;
        }
        Block* q = tail->next;            // current node at tail
        q->next = popped;                 // q now points to popped
        popped->prev = tail->next;        // re-read of p->next; unchanged by
                                          // the q->next write above (different
                                          // address). Equals q.
    } else {
        *heap_other_listhead = popped;
    }

    popped->next = NULL;
    tail->next = popped;
    heap_bump = (uint8_t*)popped + 0x100;

    return (Block*)((uint8_t*)popped + 8);
}
