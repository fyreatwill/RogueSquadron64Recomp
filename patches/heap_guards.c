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
    return addr >= 0x80000000U && addr < 0x80800000U && (addr & 3U) == 0;
}

#define MAX_FREE_BLOCKS (0x800000 / 0x100)
#define BLOCK_SIZE 0x100

// ORIGIN: func_8002221C and the free-list link stores publish block bases;
// every block dereference below reads the fixed 0x100-byte allocator object.
// A KSEG0 base in the final 0xFF bytes is not a legitimate complete block.
static int block_ok(const void* p) {
    uintptr_t addr = (uintptr_t)p;
    // ORIGIN: func_8002221C and the free-list link stores publish fixed-size
    // 0x100-byte allocator blocks. A KSEG0 pointer with another base
    // alignment cannot identify one of those blocks.
    return kseg0_ok(p) && (addr & (BLOCK_SIZE - 1U)) == 0 &&
           addr <= (0x80800000U - BLOCK_SIZE);
}

// ORIGIN: the allocator publishes heap_bump as the byte immediately after
// the block returned by this function. A non-null value outside the RDRAM
// KSEG0 range or on a non-block boundary is not a legitimate bump cursor;
// reject it before the active-queue stores can publish another allocation.
static int bump_cursor_ok(const void* p) {
    if (p == NULL) {
        return 1;
    }
    uintptr_t addr = (uintptr_t)p;
    return kseg0_ok(p) && (addr & (BLOCK_SIZE - 1U)) == 0 &&
           addr <= 0x80800000U;
}

// ORIGIN: heap_other_listhead and heap_tail_loc are fixed linker-published
// metadata slots, not heap objects. Accepting any aligned KSEG0 address here
// would let a corrupted slot pointer redirect the queue-link stores into a
// legitimate but unrelated RDRAM object.
static int metadata_slot_ok(const void* p, const void* expected) {
    return p == expected;
}

// ORIGIN: the allocator publishes each free-list node's prev link when it
// links a block. The head is the list sentinel and must have no predecessor;
// a non-null or foreign predecessor is not legitimate list state.
static int free_head_link_ok(const Block* head) {
    if (head == NULL || head->prev != NULL) {
        return head == NULL;
    }
    return head->next == NULL ||
           (block_ok(head->next) && head->next->prev == head);
}

// ORIGIN: func_8002221C and the allocator's free-list link stores publish
// every successor and predecessor. A valid list must remain reciprocal for
// its whole bounded chain; checking only the head leaves a later cycle or
// foreign link available to the next dequeue.
static int free_chain_links_ok(const Block* head) {
    const Block* node = head;
    uint32_t count = 0;
    while (node != NULL) {
        if (!block_ok(node) || node->prev != NULL &&
            (!block_ok(node->prev) || node->prev->next != node)) {
            return 0;
        }
        if (node->next == NULL) {
            return 1;
        }
        if (++count >= MAX_FREE_BLOCKS || !block_ok(node->next) ||
            node->next->prev != node) {
            return 0;
        }
        node = node->next;
    }
    return 1;
}

// ORIGIN: the active-queue insertion stores q->next and popped->prev as a
// linked pair. A non-head predecessor must already point back to q; otherwise
// the next insertion would publish a queue with a broken ownership chain.
static int active_queue_link_ok(const Block* queue_head, const Block* q) {
    if (queue_head == NULL || q == NULL || !block_ok(queue_head) ||
        !block_ok(q) || queue_head->prev != NULL) {
        return 0;
    }
    // ORIGIN: the active-queue insertion path publishes q->next only after
    // q is the current terminal node (the predecessor held by
    // heap_tail_loc). A non-null successor means the tail metadata and the
    // queue contents disagree, so appending would orphan an existing chain.
    if (q->next != NULL) {
        return 0;
    }
    return q->prev == NULL ||
           (block_ok(q->prev) && q->prev->next == q);
}

// ORIGIN: heap_tail_loc supplies the predecessor used by the append stores;
// the terminal node reached through it must point back to that same metadata
// node. A detached tail would otherwise let the append splice two unrelated
// queue chains together while every individual pointer still looks valid.
static int active_queue_tail_anchor_ok(const Block* queue_head,
                                       const Block* tail,
                                       const Block* q) {
    if (queue_head == NULL || tail == NULL || q == NULL ||
        !block_ok(queue_head) || !block_ok(tail) || !block_ok(q) ||
        tail == q || tail->next != q) {
        return 0;
    }
    if (q == queue_head) {
        return q->prev == NULL;
    }
    return q->prev == tail;
}

// ORIGIN: the empty active-queue append publishes the first node through
// heap_other_listhead and tail->next. With both publications empty, the
// sentinel tail has no active-queue predecessor; a predecessor here would
// leave an unowned link behind the published empty head.
static int active_queue_empty_tail_ok(const Block* tail) {
    return tail != NULL && block_ok(tail) && tail->prev == NULL &&
           tail->next == NULL;
}

// ORIGIN: heap_tail_loc publishes the active-queue sentinel used by both
// append paths. The sentinel is the predecessor anchor, not an active node;
// a predecessor link would give it an owner in the queue chain and make the
// next append mutate through two ownership domains.
static int active_queue_sentinel_link_ok(const Block* tail) {
    return tail != NULL && block_ok(tail) && tail->prev == NULL;
}

// ORIGIN: the active-queue insertion consumes the chain rooted at
// heap_other_listhead and appends through its terminal node. The existing
// tail check validates only that terminal node; it does not prove that the
// terminal is reachable from the published head. A bounded walk rejects
// cycles or detached tails before the link stores run.
static int active_queue_chain_ok(const Block* queue_head,
                                 const Block* q) {
    const Block* node = queue_head;
    const Block* prev = NULL;
    uint32_t count = 0;

    while (node != NULL && count++ < MAX_FREE_BLOCKS) {
        if (!block_ok(node) || node->prev != prev) {
            return 0;
        }
        if (node == q) {
            return node->next == NULL;
        }
        prev = node;
        node = node->next;
    }
    return 0;
}

// ORIGIN: heap_tail_loc publishes the active-queue sentinel used by the
// append stores. The sentinel is metadata ownership, not an active block;
// accepting it in the published chain would let a later append mutate the
// sentinel through the node-link path.
static int active_queue_sentinel_disjoint(const Block* queue_head,
                                          const Block* sentinel) {
    const Block* node = queue_head;
    uint32_t count = 0;
    while (node != NULL && count++ < MAX_FREE_BLOCKS) {
        if (!block_ok(node)) {
            return 0;
        }
        if (node == sentinel) {
            return 0;
        }
        node = node->next;
    }
    return node == NULL;
}

// ORIGIN: the free-list dequeue publishes popped as an active-queue node;
// a node already reachable from the published queue still belongs to that
// queue, so accepting the alias would create a cycle or duplicate ownership.
static int active_queue_disjoint(const Block* queue_head,
                                 const Block* popped) {
    const Block* node = queue_head;
    uint32_t count = 0;

    while (node != NULL && count++ < MAX_FREE_BLOCKS) {
        if (!block_ok(node)) {
            return 0;
        }
        if (node == popped) {
            return 0;
        }
        node = node->next;
    }
    return node == NULL;
}

// ORIGIN: func_8002221C publishes every node in an expansion chain before the
// dequeue splices that chain into heap_free_head. A node already owned by the
// active queue is not a legitimate expansion result; linking through it would
// mutate the active queue while validating the new free-list chain.
static int expansion_chain_disjoint_from_active(const Block* expansion,
                                                const Block* queue_head) {
    const Block* node = expansion;
    uint32_t count = 0;
    while (node != NULL && count++ < MAX_FREE_BLOCKS) {
        if (!block_ok(node)) {
            return 0;
        }
        if (active_queue_disjoint(queue_head, node) == 0) {
            return 0;
        }
        if (node->next != NULL && !block_ok(node->next)) {
            return 0;
        }
        node = node->next;
    }
    return node == NULL;
}

// ORIGIN: func_8002221C publishes the expansion head with no predecessor and
// links each successor back to its owning block. A foreign predecessor would
// let the free-list splice overwrite an unrelated owner through next/prev.
static int expansion_chain_links_ok(const Block* expansion) {
    const Block* node = expansion;
    const Block* prev = NULL;
    uint32_t count = 0;

    while (node != NULL && count++ < MAX_FREE_BLOCKS) {
        if (!block_ok(node) || node->prev != prev) {
            return 0;
        }
        if (node->next != NULL &&
            (!block_ok(node->next) || node->next->prev != node)) {
            return 0;
        }
        prev = node;
        node = node->next;
    }
    return node == NULL;
}

// ORIGIN: the free-list link stores own the chain rooted at heap_free_head,
// while the active-queue link stores own the chain ending at q. For two
// valid acyclic singly-linked chains, any shared node implies a shared tail;
// rejecting that tail alias closes the cross-owner case without a quadratic
// walk of both chains.
static int free_chain_disjoint_from_active_tail(const Block* free_head,
                                                const Block* active_tail) {
    const Block* node = free_head;
    uint32_t count = 0;
    while (node != NULL && count++ < MAX_FREE_BLOCKS) {
        if (node == active_tail) {
            return 0;
        }
        node = node->next;
    }
    return node == NULL;
}

// ORIGIN: the free-list link stores own the chain rooted at heap_free_head,
// while the active queue publishes every node from heap_other_listhead. A
// tail-only comparison misses an alias at an earlier active node, which can
// make the next queue append mutate a block still owned by the free list.
static int free_chain_disjoint_from_active_queue(const Block* free_head,
                                                 const Block* queue_head) {
    const Block* active = queue_head;
    uint32_t active_count = 0;

    while (active != NULL && active_count++ < MAX_FREE_BLOCKS) {
        const Block* free_node = free_head;
        uint32_t free_count = 0;
        while (free_node != NULL && free_count++ < MAX_FREE_BLOCKS) {
            if (free_node == active) {
                return 0;
            }
            if (!block_ok(free_node)) {
                return 0;
            }
            free_node = free_node->next;
        }
        if (free_node != NULL) {
            return 0;
        }
        if (!block_ok(active)) {
            return 0;
        }
        active = active->next;
    }
    return active == NULL;
}

// ORIGIN: the free-list link stores own every node reachable from
// heap_free_head; heap_tail_loc owns the active-queue sentinel. Sharing that
// sentinel between the two ownership domains would let a later dequeue
// rewrite active-queue metadata through the free-list path.
static int free_chain_disjoint_from_active_sentinel(const Block* free_head,
                                                    const Block* sentinel) {
    const Block* node = free_head;
    uint32_t count = 0;
    while (node != NULL && count++ < MAX_FREE_BLOCKS) {
        if (node == sentinel) {
            return 0;
        }
        if (!block_ok(node)) {
            return 0;
        }
        node = node->next;
    }
    return node == NULL;
}

RECOMP_PATCH Block* func_80007D74(void) {
    Block* head = heap_free_head;

    // If the free list is empty, allocate a new chunk (which itself is a
    // chain of free blocks linked via .next) and prepend it to the list.
    if (head == NULL) {
        Block* fresh = func_8002221C();
        if (fresh != NULL) {
            if (!block_ok(fresh)) {
                return NULL;
            }
            if (!expansion_chain_links_ok(fresh)) {
                return NULL;
            }
            if (metadata_slot_ok(heap_other_listhead, (void*)0x801163FC)) {
                Block* active_head = *heap_other_listhead;
                if (active_head != NULL &&
                    !expansion_chain_disjoint_from_active(fresh, active_head)) {
                    return NULL;
                }
            }
            // Walk fresh's chain to find its tail
            Block* tail = fresh;
            uint32_t chain_len = 0;
            while (tail->next != NULL) {
                if (++chain_len >= MAX_FREE_BLOCKS) {
                    return NULL;
                }
                if (!block_ok(tail->next)) {
                    return NULL;
                }
                if (tail->next->prev != tail) {
                    return NULL;
                }
                tail = tail->next;
            }
            // Splice old head onto the end of fresh's chain
            Block* old_head = heap_free_head;
            if (old_head == NULL) {
                tail->next = NULL;
            } else {
                if (!block_ok(old_head)) {
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
    if (!block_ok(head)) {
        new_head = NULL;
    } else if (!free_head_link_ok(head) || !free_chain_links_ok(head)) {
        return NULL;
    } else {
        new_head = head->next;
    }
    heap_free_head = new_head;
    if (block_ok(new_head)) {
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

    if (!block_ok(popped)) {
        return NULL;
    }

    if (!bump_cursor_ok(heap_bump)) {
        return NULL;
    }

    // Insert popped into the active queue only after validating the value
    // published by the free-list head.
    if (!metadata_slot_ok(heap_other_listhead, (void*)0x801163FC) ||
        !metadata_slot_ok(heap_tail_loc, (void*)0x8011A7DC)) {
        return NULL;
    }
    Block* tail = *heap_tail_loc;
    if (!block_ok(tail)) {
        return NULL;
    }
    if (!active_queue_sentinel_link_ok(tail)) {
        return NULL;
    }

    if (!free_chain_disjoint_from_active_sentinel(head, tail)) {
        return NULL;
    }

    // ORIGIN: the free-list dequeue publishes `popped`; the active-queue
    // append consumes `tail`. In an empty published queue, they cannot be
    // the same allocator object without claiming one block in two owners.
    if (popped == tail) {
        return NULL;
    }

    Block* queue_head = *heap_other_listhead;
    if (queue_head != NULL && !block_ok(queue_head)) {
        return NULL;
    }

    // ORIGIN: the free-list dequeue publishes `popped`, while the active
    // queue head owns its reachable nodes. These are distinct ownership
    // domains; aliasing the head would make the append read a free-list node
    // as an active-queue predecessor before the later disjointness check.
    if (queue_head == popped) {
        return NULL;
    }

    // ORIGIN: heap_free_head and heap_other_listhead publish separate owner
    // chains. The existing tail comparison does not reject an overlap at an
    // earlier active node, so audit the complete bounded active chain before
    // publishing another link.
    if (queue_head != NULL &&
        !free_chain_disjoint_from_active_queue(head, queue_head)) {
        return NULL;
    }

    // ORIGIN: the active-queue append publishes tail->next and the head slot
    // as one chain. A null published head with an existing successor is a
    // detached queue, not a legitimate empty-list state.
    if (queue_head == NULL && tail->next != NULL) {
        return NULL;
    }

    if (queue_head == NULL && !active_queue_empty_tail_ok(tail)) {
        return NULL;
    }

    if (queue_head != NULL) {
        // Queue non-empty — append after current node.
        if (!block_ok(tail->next)) {
            return NULL;
        }
        Block* q = tail->next;            // current node at tail

        if (!active_queue_link_ok(queue_head, q)) {
            return NULL;
        }
        if (!active_queue_tail_anchor_ok(queue_head, tail, q)) {
            return NULL;
        }
        if (!active_queue_chain_ok(queue_head, q) || tail->next != q) {
            return NULL;
        }
        if (!active_queue_sentinel_disjoint(queue_head, tail)) {
            return NULL;
        }

        if (popped == tail || !active_queue_disjoint(queue_head, popped) ||
            !free_chain_disjoint_from_active_tail(head, q)) {
            return NULL;
        }

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
