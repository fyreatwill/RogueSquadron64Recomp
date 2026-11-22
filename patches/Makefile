TARGET = patches.elf

# Default toolchain. Override on cmdline if your install lives elsewhere:
#   make CC="C:/mips-toolchain/bin/mips64-elf-gcc.exe" LD="C:/mips-toolchain/bin/mips64-elf-ld.exe"
# The CMake integration sets these absolute paths automatically.
# make's built-in CC=cc has 'default' origin, so '?=' never applied; override it explicitly.
ifeq ($(origin CC),default)
CC := mips64-elf-gcc
endif
ifeq ($(origin LD),default)
LD := mips64-elf-ld
endif
AS      ?= mips-linux-gnu-as

# Adapted from Zelda64Recompiled/patches/Makefile, gcc flavor.
# -G0 disables small-data optimization (we don't have a $gp setup in
# the patch ELF). -mno-abicalls avoids PIC code (relocs we don't want).
# -mips2 -mabi=32 produce N64-compatible 32-bit MIPS code even with the
# mips64-elf-gcc toolchain.
CFLAGS   := -mips2 -mabi=32 -O2 -G0 -mno-abicalls \
            -fomit-frame-pointer -ffast-math -fno-unsafe-math-optimizations -fno-builtin-memset \
            -Wall -Wextra -Wno-unused-parameter -Wno-unknown-pragmas -Wno-unused-variable \
            -Wno-missing-braces
CPPFLAGS := -nostdinc -D_LANGUAGE_C -DMIPS \
            -I dummy_headers \
            -I ../lib/N64ModernRuntime/librecomp/include
LDFLAGS  := -nostdlib -T patches.ld -T syms.ld -Map patches.map \
            --unresolved-symbols=ignore-all --emit-relocs

C_SRCS := $(wildcard *.c)
C_OBJS := $(C_SRCS:.c=.o)
C_DEPS := $(C_SRCS:.c=.d)

# ASM_ONLY is used for bounded assembly-port validation. It intentionally
# excludes the C override so both implementations do not define the same
# patch symbol in one ELF.
ifeq ($(ASM_ONLY),1)
C_SRCS :=
C_OBJS :=
C_DEPS :=
ASM_SRCS := $(wildcard *.S)
ASM_OBJS := $(ASM_SRCS:.S=.o)
else
ASM_SRCS :=
ASM_OBJS :=
endif

# Allow build with no source files yet — produces an empty patches.elf so
# the rest of the toolchain (recomp, linker) can still wire up.
ifeq ($(C_SRCS),)
ifneq ($(ASM_ONLY),1)
EMPTY_DUMMY := __empty_patches.c
$(EMPTY_DUMMY):
	@echo "// Auto-generated placeholder so make has something to compile" > $@
	@echo "void __patches_placeholder(void) { }" >> $@
C_SRCS := $(EMPTY_DUMMY)
C_OBJS := $(EMPTY_DUMMY:.c=.o)
C_DEPS := $(EMPTY_DUMMY:.c=.d)
endif
endif

$(TARGET): $(C_OBJS) $(ASM_OBJS) patches.ld syms.ld
	$(LD) $(C_OBJS) $(ASM_OBJS) $(LDFLAGS) -o $@

# s7806: objects depend on the toolchain identity (compiler --version + flags). Before this, a heap_guards.o built by the
# clang wrapper that briefly answered to mips64-elf-gcc (2026-10-17) stayed in every build, so the owner's binary carried
# patch code no clean build reproduces. .toolchain_id is rewritten only when the identity changes.
TOOLCHAIN_ID := $(shell $(CC) --version 2>/dev/null | head -1) | $(CFLAGS) $(CPPFLAGS)
.toolchain_id: FORCE
	@echo '$(TOOLCHAIN_ID)' | cmp -s - $@ || echo '$(TOOLCHAIN_ID)' > $@

$(C_OBJS): %.o : %.c .toolchain_id
	$(CC) $(CFLAGS) $(CPPFLAGS) $< -MMD -MF $(@:.o=.d) -c -o $@

$(ASM_OBJS): %.o : %.S
	$(AS) -mips2 -mabi=32 -EB -o $@ $<

clean:
	rm -rf $(C_OBJS) $(ASM_OBJS) $(TARGET) $(C_DEPS) patches.map __empty_patches.c .toolchain_id

-include $(C_DEPS)

.PHONY: clean FORCE
FORCE:
