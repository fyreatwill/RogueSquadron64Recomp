#define main oracle_main
#include "rs64_oracle.c"
#undef main
#include <assert.h>

int main(void)
{
    for (unsigned lane = 0; lane < 4; lane++) {
        uint32_t mask = scalar_store_mask(0x28u << 26, lane);
        assert(mask == (0xFFu << ((3u - lane) * 8u)));
        assert(scalar_store_expected(mask, 0x123456ABu) ==
               (0xABu << ((3u - lane) * 8u)));
        struct post_value_pc_entry entry = {0};
        g_post_store_mask = mask;
        g_post_store_expected = 0;
        count_scalar_store(&entry, ~mask);
        assert(entry.scalar_zero == 1 && entry.scalar_mismatch == 0);
        count_scalar_store(&entry, UINT32_MAX);
        assert(entry.scalar_nonzero == 1 && entry.scalar_mismatch == 1);
    }
    assert(scalar_store_mask(0x29u << 26, 0) == 0xFFFF0000u);
    assert(scalar_store_mask(0x29u << 26, 2) == 0x0000FFFFu);
    assert(scalar_store_mask(0x29u << 26, 1) == 0);
    assert(scalar_store_mask(0x29u << 26, 3) == 0);
    assert(scalar_store_expected(0xFFFF0000u, 0x1234ABCDu) == 0xABCD0000u);
    assert(scalar_store_expected(0x0000FFFFu, 0x1234ABCDu) == 0x0000ABCDu);
    assert(scalar_store_mask(0x2Bu << 26, 0) == UINT32_MAX);
    assert(scalar_store_mask(0x2Bu << 26, 1) == 0);
    assert(scalar_store_mask(0x2Au << 26, 0) == 0);
    assert(scalar_store_expected(UINT32_MAX, 0x12345678u) == 0x12345678u);
    assert(scalar_store_expected(0, UINT32_MAX) == 0);
    puts("store sample tests passed");
    return 0;
}
