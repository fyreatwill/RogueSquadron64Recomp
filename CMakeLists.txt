cmake_minimum_required(VERSION 3.20)

if (APPLE)
    set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0" CACHE STRING "Minimum OS X deployment version")
endif()

project(RogueSquadron64Recomp LANGUAGES C CXX)
set(CMAKE_C_STANDARD 17)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if (WIN32)
    add_compile_definitions(NOMINMAX _DISABLE_CONSTEXPR_MUTEX_CONSTRUCTOR)
endif()

# Disable MSVC's debug iterator bounds checks. Currently there's a
# `vector subscript out of range` assert deep in RT64 when Factor 5's
# ucode generates non-standard RDP byte sequences. The assert fires in
# Debug builds even with our CRT_REPORT hook returning 1 because
# _STL_VERIFY calls abort() unconditionally after the report. With
# bounds checks off, the vector returns garbage and execution continues.
# Trade-off: we lose bounds-check safety nets across the whole build.
# Enable via -DROGUESQ_NO_ITER_DEBUG=ON. Both defines are required to
# avoid linker incompatibility with already-compiled debug libs.
option(ROGUESQ_NO_ITER_DEBUG "Disable MSVC debug iterators (skip bounds checks)" OFF)
if(WIN32 AND ROGUESQ_NO_ITER_DEBUG)
    add_compile_definitions(_HAS_ITERATOR_DEBUGGING=0 _ITERATOR_DEBUG_LEVEL=0)
    message(STATUS "MSVC debug iterators DISABLED (vector bounds checks off)")
endif()

if (APPLE)
    enable_language(OBJC OBJCXX)
endif()

if (CMAKE_VERSION VERSION_GREATER_EQUAL "3.24.0")
    cmake_policy(SET CMP0135 NEW)
endif()

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

# ---- RT64 renderer ----
set(RT64_STATIC TRUE)
set(RT64_SDL_WINDOW_VULKAN TRUE)
add_compile_definitions(HLSL_CPU)
# Enable D3D12 debug layer to get readable error messages from DirectX
# instead of cryptic crashes deep in D3D12GetInterface. RT64's plume layer
# checks for D3D12_DEBUG_LAYER_ENABLED at compile time. Set via
# -DROGUESQ_DX12_DEBUG=ON when configuring CMake to enable.
option(ROGUESQ_DX12_DEBUG "Enable D3D12 debug layer in RT64" OFF)
if(ROGUESQ_DX12_DEBUG)
    add_compile_definitions(D3D12_DEBUG_LAYER_ENABLED)
    message(STATUS "D3D12 debug layer ENABLED")
endif()
# s4907: the Debug config is a bare "-g" (-O0) and RT64 inherited it. Measured at -O0:
# State::updateScreen spends 1.6 ms in a 344 KB vector resize and 1.1 ms in a 344 KB XXH3 hash
# (~0.3 GB/s) -- ~30x off a Fermi estimate -- and the gfx task takes ~21 ms. RT64 is host code
# with no recompiled-guest semantics, so optimise it; ROGUESQ_RT64_OPT=OFF restores -O0.
option(ROGUESQ_RT64_OPT "Compile RT64 (host renderer) with -O2 under the Debug config" ON)
add_subdirectory(${CMAKE_SOURCE_DIR}/lib/rt64 ${CMAKE_BINARY_DIR}/rt64)
if (ROGUESQ_RT64_OPT AND NOT MSVC)
    # Target-scoped on purpose: a global flag change also rebuilds the shader helper tools, which
    # regenerates every shader and needs the Metal toolchain.
    target_compile_options(rt64 PRIVATE -O2)
endif()
# s6935: plume (RT64's Metal wrapper) is a separate target, so ROGUESQ_RT64_OPT missed it and it stayed -O0: every encoded
# draw state check ran as unoptimised std::vector and __wrap_iter calls on the RT64 threads. Same reasoning as above.
option(ROGUESQ_PLUME_OPT "Compile plume (RT64 Metal wrapper) with -O2 under the Debug config" ON)
if (ROGUESQ_PLUME_OPT AND NOT MSVC)
    target_compile_options(plume PRIVATE -O2)
endif()

# ---- N64ModernRuntime (ultramodern + librecomp) ----
add_subdirectory(${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime ${CMAKE_BINARY_DIR}/N64ModernRuntime)

# ---- RecompiledFuncs ----
# Path to the N64Recomp output — adjust if you move the files
# s7406: overridable so a diagnostic build dir can compile a transformed copy (tools/build_fpat.sh). build/ never sets it.
if (NOT DEFINED RECOMP_FUNCS_DIR)
    set(RECOMP_FUNCS_DIR "${CMAKE_SOURCE_DIR}/../N64Recomp/RecompiledFuncs")
endif()

add_library(RecompiledFuncs STATIC)

if (MSVC)
    target_compile_options(RecompiledFuncs PRIVATE /wd4101 /wd4133)
    # ClangCL: the recompiler emits calls to libultra *_recomp wrappers whose
    # declarations live in the runtime, not funcs.h. Treat implicit decls as a
    # warning instead of an error (plain MSVC cl ignores this flag).
    target_compile_options(RecompiledFuncs PRIVATE
        -Wno-implicit-function-declaration
        -Wno-error=implicit-function-declaration)
    # Force-include our MEM_WU macro header (fills the unsigned-word gap in
    # upstream recomp.h without modifying it). See include/rsp_dpc_macros.h.
    target_compile_options(RecompiledFuncs PRIVATE
        /FI${CMAKE_SOURCE_DIR}/include/rsp_dpc_macros.h)
    # Rename game's 'main' to avoid MSVC treating it as the entry point
    target_compile_definitions(RecompiledFuncs PRIVATE main=rs_main)
else()
    target_compile_definitions(RecompiledFuncs PRIVATE main=rs_main)
    target_compile_options(RecompiledFuncs PRIVATE
        -fno-strict-aliasing
        -Wno-unused-variable
        -Wno-implicit-function-declaration
        -include ${CMAKE_SOURCE_DIR}/include/rsp_dpc_macros.h
    )
endif()

# s5690 bool-store watch (recomp.h MEM_B -> rs64_bwatch, env ROGUESQ_BOOLSTORE_WATCH=1). Was defined unconditionally since
# s5690; s7425 (class CH) found it the only diagnostic define live in build/: identity unless the env is set, but an inlined
# static load + test on every guest byte access (+2.5% __text in funcs_9) and no remaining consumer. OFF = shipped build.
option(ROGUESQ_BYTE_WATCH "s5690 diagnostic: log guest byte stores into 0x8013889F..0x8013891E" OFF)
if (ROGUESQ_BYTE_WATCH AND NOT MSVC)
    target_compile_definitions(RecompiledFuncs PRIVATE RS64_BYTE_WATCH)
endif()

# s7389: framebuffer-load watch (separate build dir only, tools/build_fbld.sh). include/fbld/recomp.h wraps the guest
# MEM_* macros so every access to a page named by SetColorImage/SetZImage is reported. Never ON in build/.
option(ROGUESQ_FB_LDWATCH "s7389 diagnostic: report guest loads from framebuffer pages" OFF)
if (ROGUESQ_FB_LDWATCH)
    target_include_directories(RecompiledFuncs BEFORE PRIVATE ${CMAKE_SOURCE_DIR}/include/fbld)
    target_compile_definitions(RecompiledFuncs PRIVATE RS64_FB_LDWATCH)
endif()

# s7391: guest stack low-water watch (separate build dir only, tools/build_spwm.sh). include/spwm/recomp.h routes every
# generated `ctx->r29 = ADD32(ctx->r29, ...)` through a per-thread minimum-$sp check. Never ON in build/.
option(ROGUESQ_SP_WATCH "s7391 diagnostic: per-thread guest stack low-water marks" OFF)
if (ROGUESQ_SP_WATCH)
    target_include_directories(RecompiledFuncs BEFORE PRIVATE ${CMAKE_SOURCE_DIR}/include/spwm)
    target_compile_definitions(RecompiledFuncs PRIVATE RS64_SP_WATCH)
endif()

target_include_directories(RecompiledFuncs PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/ultramodern/include
    ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/librecomp/include
    ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/N64Recomp/include
)

# CONFIGURE_DEPENDS: N64Recomp splits funcs_*.c into more files as the
# generated function count grows (s401 -- a large enough regen spawned
# funcs_45.c..funcs_50.c mid-session). A plain file(GLOB) only re-scans the
# directory at configure time, so `cmake --build` alone after such a regen
# silently links against a stale file list and produces spurious "undefined
# symbol" link errors for functions that in fact exist on disk. This costs a
# `cmake -S . -B build` reconfigure (not just --build) after any regen that
# changes the RecompiledFuncs file count; CONFIGURE_DEPENDS makes CMake
# re-glob automatically instead.
file(GLOB RECOMP_C_SOURCES   CONFIGURE_DEPENDS ${RECOMP_FUNCS_DIR}/*.c)
file(GLOB RECOMP_CXX_SOURCES CONFIGURE_DEPENDS ${RECOMP_FUNCS_DIR}/*.cpp)
target_sources(RecompiledFuncs PRIVATE ${RECOMP_C_SOURCES} ${RECOMP_CXX_SOURCES})

# ---- Patches (Zelda-style override layer) ----
# Hand-written C in patches/*.c is cross-compiled to MIPS by the decompals
# mips64-elf-gcc toolchain, then run back through N64Recomp to produce
# RecompiledPatches/patches.c. Symbols defined there override the same names
# in RecompiledFuncs because PatchesLib gets linked first. Pattern adapted
# from Zelda64Recompiled — see docs/audit-changes.md Tier 4 + patches/README.md.

set(PATCHES_DIR             "${CMAKE_SOURCE_DIR}/patches")
set(RECOMPILED_PATCHES_DIR  "${CMAKE_SOURCE_DIR}/RecompiledPatches")

# Toolchain locations. Override on the cmake command line if installed elsewhere:
#   cmake -DMIPS_TOOLCHAIN_DIR=C:/mips-toolchain ...
set(MIPS_TOOLCHAIN_DIR "E:/mips-toolchain" CACHE PATH "Root of mips64-elf toolchain (decompals/n64-tools).")
if (WIN32)
    set(_MIPS_GCC_NAME mips64-elf-gcc.exe)
    set(_MIPS_LD_NAME  mips64-elf-ld.exe)
    set(_N64RECOMP_NAME N64Recomp.exe)
else()
    set(_MIPS_GCC_NAME mips64-elf-gcc)
    set(_MIPS_LD_NAME  mips64-elf-ld)
    set(_N64RECOMP_NAME N64Recomp)
endif()
set(MIPS_GCC           "${MIPS_TOOLCHAIN_DIR}/bin/${_MIPS_GCC_NAME}" CACHE FILEPATH
    "MIPS C compiler used to build the patch ELF")
set(MIPS_LD            "${MIPS_TOOLCHAIN_DIR}/bin/${_MIPS_LD_NAME}" CACHE FILEPATH
    "MIPS linker used to build the patch ELF")
if (NOT EXISTS "${MIPS_GCC}" OR NOT EXISTS "${MIPS_LD}")
    find_program(_MIPS_GCC_ON_PATH NAMES mips64-elf-gcc)
    find_program(_MIPS_LD_ON_PATH  NAMES mips64-elf-ld)
    if (_MIPS_GCC_ON_PATH AND _MIPS_LD_ON_PATH)
        set(MIPS_GCC "${_MIPS_GCC_ON_PATH}")
        set(MIPS_LD  "${_MIPS_LD_ON_PATH}")
    endif()
endif()
set(_N64RECOMP_DEFAULT "${CMAKE_BINARY_DIR}/${_N64RECOMP_NAME}")
if (NOT DEFINED N64RECOMP_EXE OR NOT EXISTS "${N64RECOMP_EXE}")
    set(N64RECOMP_EXE "${_N64RECOMP_DEFAULT}" CACHE FILEPATH
        "N64Recomp executable (built from lib/N64ModernRuntime/N64Recomp via N64RecompCLI target)" FORCE)
endif()
find_program(PATCHES_MAKE_EXE NAMES mingw32-make make)
find_package(Python3 COMPONENTS Interpreter)

if (EXISTS "${MIPS_GCC}" AND EXISTS "${N64RECOMP_EXE}" AND PATCHES_MAKE_EXE AND Python3_Interpreter_FOUND)
    file(GLOB PATCH_C_SOURCES "${PATCHES_DIR}/*.c")

    # Step 1: cross-compile *.c → patches.elf (MIPS)
    add_custom_command(OUTPUT "${PATCHES_DIR}/patches.elf"
        COMMAND ${PATCHES_MAKE_EXE} CC=${MIPS_GCC} LD=${MIPS_LD}
        WORKING_DIRECTORY "${PATCHES_DIR}"
        # s7806: the compiler is an input too. A clang-built heap_guards.o (Oct 17, before mips64-elf-gcc replaced the
        # clang wrapper at the same path) survived 5 weeks because nothing re-ran make; patches/Makefile also stamps it.
        DEPENDS ${PATCH_C_SOURCES} "${MIPS_GCC}"
                "${PATCHES_DIR}/Makefile"
                "${PATCHES_DIR}/patches.ld"
                "${PATCHES_DIR}/syms.ld"
        COMMENT "Cross-compiling patches.elf (MIPS)"
        VERBATIM
    )

    # Step 2: N64Recomp the elf → RecompiledPatches/patches.c
    add_custom_command(OUTPUT "${RECOMPILED_PATCHES_DIR}/patches.c"
                              "${RECOMPILED_PATCHES_DIR}/funcs.h"
                              "${RECOMPILED_PATCHES_DIR}/recomp_overlays.inl"
        COMMAND ${N64RECOMP_EXE} "${CMAKE_SOURCE_DIR}/patches.toml"
        COMMAND ${Python3_EXECUTABLE} "${CMAKE_SOURCE_DIR}/tools/fixup_patches_host.py"
                "${RECOMPILED_PATCHES_DIR}/patches.c"
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
        DEPENDS "${PATCHES_DIR}/patches.elf" "${CMAKE_SOURCE_DIR}/patches.toml"
                "${CMAKE_SOURCE_DIR}/tools/fixup_patches_host.py"
        COMMENT "Recompiling patches.elf → RecompiledPatches/patches.c"
        VERBATIM
    )

    # Step 3: build PatchesLib that wraps the recompiled output
    add_library(PatchesLib STATIC "${RECOMPILED_PATCHES_DIR}/patches.c")
    set_source_files_properties("${RECOMPILED_PATCHES_DIR}/patches.c"
        PROPERTIES GENERATED TRUE)

    target_include_directories(PatchesLib PRIVATE
        ${CMAKE_SOURCE_DIR}/include
        ${RECOMPILED_PATCHES_DIR}
        ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/ultramodern/include
        ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/librecomp/include
        ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/N64Recomp/include
    )
    if (MSVC)
        target_compile_options(PatchesLib PRIVATE /wd4101 /wd4133
            -Wno-implicit-function-declaration
            -Wno-error=implicit-function-declaration)
    else()
        target_compile_options(PatchesLib PRIVATE
            -fno-strict-aliasing -Wno-unused-variable -Wno-implicit-function-declaration)
    endif()
    target_compile_definitions(PatchesLib PRIVATE main=rs_main)
    if (ROGUESQ_SP_WATCH)
        target_include_directories(PatchesLib BEFORE PRIVATE ${CMAKE_SOURCE_DIR}/include/spwm)
        target_compile_definitions(PatchesLib PRIVATE RS64_SP_WATCH)
    endif()

    set(PATCHES_BUILD_OK TRUE)
else()
    set(PATCHES_BUILD_OK FALSE)
    message(STATUS "Patches build skipped:")
    if (NOT EXISTS "${MIPS_GCC}")
        message(STATUS "  - mips64-elf-gcc not at ${MIPS_GCC}")
    endif()
    if (NOT EXISTS "${N64RECOMP_EXE}")
        message(STATUS "  - N64Recomp.exe not at ${N64RECOMP_EXE}")
    endif()
    if (NOT PATCHES_MAKE_EXE)
        message(STATUS "  - mingw32-make / make not on PATH")
    endif()
    message(STATUS "  See patches/README.md for setup; rebuild without patches for now.")
endif()

# ---- Main executable ----
# Hybrid graphics pipeline (2026-05-09):
#   - HLE side: RT64's Factor 5 GBI module (lib/rt64/src/gbi/rt64_gbi_f3dfactor5.cpp)
#     handles standard F3D-derived opcodes (TEXRECT, FILLRECT, sync ops, etc.)
#     when the HLE path is invoked.
#   - LLE side: factor5_ucode_recompiled.c (auto-translated by RSPRecomp from the
#     game's RSP graphics ucode) handles vertex transform / clip / project.
#     Triangles get emitted as raw RDP bytes via DPC_END writes; src/rsp/
#     dpc_bridge.cpp forwards them into RT64 via submit_rdp_range.
#
# A pure HLE replacement for the LLE side is feasible (op_01..op_04 plus
# triangle assembly are tractable handlers, contrary to factor5-gbi.md's
# original "GBI-level plan is closed" conclusion) but is multi-day work.
# Keeping LLE for now lets us ship visuals while migrating ops one at a time.
set(FACTOR5_UCODE_C ${CMAKE_SOURCE_DIR}/build/factor5_ucode/factor5_ucode_recompiled.c)
# Audio RSP image labelled aspMainText (RDRAM 0x80099FE0, ROM 0x9ABE0); its
# task/output ABI remains under validation (see factor5b_rsp.toml).
set(FACTOR5_UCODE_B_C ${CMAKE_SOURCE_DIR}/build/factor5_ucode/factor5_ucode_b_recompiled.c)
set(FACTOR5_BOOT_C  ${CMAKE_SOURCE_DIR}/build/factor5_ucode/factor5_boot_recompiled.c)
# Post-process: RSPRecomp emits a goto to a non-existent label for one
# never-taken branch near end-of-IMEM (perspective-divide reciprocal block).
# tools/fixup_factor5_ucode.py rewrites those gotos to clean exits. The
# fixup runs as part of CMake config so it survives any future regen.
find_package(Python3 COMPONENTS Interpreter)
if (Python3_Interpreter_FOUND AND EXISTS ${FACTOR5_UCODE_C})
    execute_process(
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/fixup_factor5_ucode.py ${FACTOR5_UCODE_C}
        RESULT_VARIABLE FACTOR5_FIXUP_RESULT
    )
    if (NOT FACTOR5_FIXUP_RESULT EQUAL 0)  # s7742: these exited 1 unseen since s4751 (fixup 24 was not scoped to the main file)
        message(WARNING "tools/fixup_factor5_ucode.py exited ${FACTOR5_FIXUP_RESULT} (FACTOR5_FIXUP_RESULT)")
    endif()
endif()
# Same fixup, applied to factor5_boot_recompiled.c. The boot ucode hands off
# to the main ucode via `jr $7=0x1080`, which RSPRecomp can't model — without
# this fixup, every task triggers a 4-line printf register dump. The runner
# already treats UnhandledJumpTarget from boot as expected, so the printf is
# pure spam (and at ~3 tasks/sec it can starve the console pump).
if (Python3_Interpreter_FOUND AND EXISTS ${FACTOR5_UCODE_B_C})
    execute_process(
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/fixup_factor5_ucode.py ${FACTOR5_UCODE_B_C}
        RESULT_VARIABLE FACTOR5_B_FIXUP_RESULT
    )
    if (NOT FACTOR5_B_FIXUP_RESULT EQUAL 0)  # s7742: these exited 1 unseen since s4751 (fixup 24 was not scoped to the main file)
        message(WARNING "tools/fixup_factor5_ucode.py exited ${FACTOR5_B_FIXUP_RESULT} (FACTOR5_B_FIXUP_RESULT)")
    endif()
endif()
if (Python3_Interpreter_FOUND AND EXISTS ${FACTOR5_BOOT_C})
    execute_process(
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/fixup_factor5_ucode.py ${FACTOR5_BOOT_C}
        RESULT_VARIABLE FACTOR5_BOOT_FIXUP_RESULT
    )
    if (NOT FACTOR5_BOOT_FIXUP_RESULT EQUAL 0)  # s7742: these exited 1 unseen since s4751 (fixup 24 was not scoped to the main file)
        message(WARNING "tools/fixup_factor5_ucode.py exited ${FACTOR5_BOOT_FIXUP_RESULT} (FACTOR5_BOOT_FIXUP_RESULT)")
    endif()
endif()
if (MSVC)
    set(RS64_UCODE_FLAGS "-msse4.1;/FI${CMAKE_SOURCE_DIR}/include/rsp_dpc_macros.h")
elseif (CMAKE_SYSTEM_PROCESSOR MATCHES "arm64|aarch64")
    set(RS64_UCODE_FLAGS "-include;${CMAKE_SOURCE_DIR}/include/rsp_dpc_macros.h")
else()
    set(RS64_UCODE_FLAGS "-msse4.1;-include;${CMAKE_SOURCE_DIR}/include/rsp_dpc_macros.h")
endif()
# Session 38: this project is configured CMAKE_BUILD_TYPE=Debug, whose flags are
# just "-g" — i.e. -O0. The recompiled ucode is one call per emulated RSP
# instruction, so unoptimised it dominates the frame (s37: 186.6 ms per hangar
# gfx task). Optimise these three translation units regardless of build type;
# set ROGUESQ_UCODE_NO_OPT=ON to restore the old behaviour for debugging.
option(ROGUESQ_UCODE_NO_OPT "Compile the recompiled RSP ucode unoptimised" OFF)
if (NOT ROGUESQ_UCODE_NO_OPT AND NOT MSVC)
    list(APPEND RS64_UCODE_FLAGS "-O2")
endif()
set_source_files_properties(${FACTOR5_UCODE_C} ${FACTOR5_UCODE_B_C} ${FACTOR5_BOOT_C} PROPERTIES
    LANGUAGE CXX
    COMPILE_OPTIONS "${RS64_UCODE_FLAGS}")
# s6714 G1e: factor5_ucode is one huge function and the RSP:: vector templates (VMADN/VMADM/VMUDL/SDV...) exceed clang's
# -O2 inline threshold, so ~250 call sites stay out-of-line bl's. A higher threshold for the gfx ucode TU only inlines
# them. s6714 interleaved A/B/A/B (lvl5 FPS60 dd4): 207.1 -> 185.3 ns per RDP cmd (-10.5%). 0 = compiler default.
set(ROGUESQ_UCODE_INLINE_THRESHOLD "4000" CACHE STRING "clang -inline-threshold for the gfx ucode TU (0 = default)")
if (NOT MSVC AND NOT ROGUESQ_UCODE_INLINE_THRESHOLD STREQUAL "0")
    set_property(SOURCE ${FACTOR5_UCODE_C} APPEND PROPERTY COMPILE_OPTIONS
        -mllvm "-inline-threshold=${ROGUESQ_UCODE_INLINE_THRESHOLD}")
endif()
# s6775 G1e: the gfx ucode runs only on the gfx thread, where g_dmem_cur == dmem, so its TU addresses DMEM through the
# link-time-constant array (rsp.hpp RS64_DMEM_BASE) and a renamed RSP type (no template merging with the audio TU, which
# must keep the per-thread base). src/rsp/factor5_ucode_tls.cpp is the same ucode on the old base, for a same-run A/B.
set_property(SOURCE ${FACTOR5_UCODE_C} APPEND PROPERTY COMPILE_DEFINITIONS RS64_DMEM_BASE=dmem RSP=RS64_RSP_GFX)
set(FACTOR5_UCODE_TLS_CPP ${CMAKE_SOURCE_DIR}/src/rsp/factor5_ucode_tls.cpp)
# s6940 G1e: lean arm, the gfx ucode with the hook/probe gates compiled to 0 (src/rsp/factor5_ucode_lean.cpp).
set(FACTOR5_UCODE_LEAN_CPP ${CMAKE_SOURCE_DIR}/src/rsp/factor5_ucode_lean.cpp)
set_source_files_properties(${FACTOR5_UCODE_LEAN_CPP} PROPERTIES COMPILE_OPTIONS "${RS64_UCODE_FLAGS}" OBJECT_DEPENDS ${FACTOR5_UCODE_C})
set_property(SOURCE ${FACTOR5_UCODE_LEAN_CPP} APPEND PROPERTY COMPILE_DEFINITIONS RS64_DMEM_BASE=dmem RSP=RS64_RSP_LEAN)
if (NOT MSVC AND NOT ROGUESQ_UCODE_INLINE_THRESHOLD STREQUAL "0")
    set_property(SOURCE ${FACTOR5_UCODE_LEAN_CPP} APPEND PROPERTY COMPILE_OPTIONS
        -mllvm "-inline-threshold=${ROGUESQ_UCODE_INLINE_THRESHOLD}")
endif()
# s6941 G1e: lean arm + native NEON multiply-op bodies (src/rsp/factor5_ucode_nmac.cpp).
set(FACTOR5_UCODE_NMAC_CPP ${CMAKE_SOURCE_DIR}/src/rsp/factor5_ucode_nmac.cpp)
set_source_files_properties(${FACTOR5_UCODE_NMAC_CPP} PROPERTIES COMPILE_OPTIONS "${RS64_UCODE_FLAGS}" OBJECT_DEPENDS ${FACTOR5_UCODE_C})
set_property(SOURCE ${FACTOR5_UCODE_NMAC_CPP} APPEND PROPERTY COMPILE_DEFINITIONS RS64_DMEM_BASE=dmem RSP=RS64_RSP_NMAC)
if (NOT MSVC AND NOT ROGUESQ_UCODE_INLINE_THRESHOLD STREQUAL "0")
    set_property(SOURCE ${FACTOR5_UCODE_NMAC_CPP} APPEND PROPERTY COMPILE_OPTIONS
        -mllvm "-inline-threshold=${ROGUESQ_UCODE_INLINE_THRESHOLD}")
endif()
set_source_files_properties(${FACTOR5_UCODE_TLS_CPP} PROPERTIES COMPILE_OPTIONS "${RS64_UCODE_FLAGS}" OBJECT_DEPENDS ${FACTOR5_UCODE_C})
if (NOT MSVC AND NOT ROGUESQ_UCODE_INLINE_THRESHOLD STREQUAL "0")
    set_property(SOURCE ${FACTOR5_UCODE_TLS_CPP} APPEND PROPERTY COMPILE_OPTIONS
        -mllvm "-inline-threshold=${ROGUESQ_UCODE_INLINE_THRESHOLD}")
endif()
# s7369: the RSP ucode TUs above are compiled as CXX, so a ThreadSanitizer build (tools/build_tsan.sh puts -fsanitize=thread
# in the CXX flags) instrumented every DMEM/RDRAM access of the gfx and audio ucode. At the dd8 21:9 1024-wide scene a gfx task
# then took ~6.1 s (median, s7369 c1) vs ~0.2 s before it, so the TSan arm crawled at ~0.1 frame/s and never reached a mission
# phase. The ucode only touches DMEM (per-thread) and guest RDRAM (shared with the guest by design, like the generated C, which
# build_tsan already leaves uninstrumented). Keep it out of TSan; ROGUESQ_TSAN_UCODE=ON restores the instrumented ucode.
if (CMAKE_CXX_FLAGS_DEBUG MATCHES "fsanitize=thread" OR CMAKE_CXX_FLAGS MATCHES "fsanitize=thread")
    option(ROGUESQ_TSAN_UCODE "Instrument the RSP ucode TUs under ThreadSanitizer" OFF)
    if (NOT ROGUESQ_TSAN_UCODE)
        set_property(SOURCE ${FACTOR5_UCODE_C} ${FACTOR5_UCODE_B_C} ${FACTOR5_BOOT_C} ${FACTOR5_UCODE_TLS_CPP}
            ${FACTOR5_UCODE_LEAN_CPP} ${FACTOR5_UCODE_NMAC_CPP} APPEND PROPERTY COMPILE_OPTIONS -fno-sanitize=thread)
        message(STATUS "s7369: RSP ucode TUs built without -fsanitize=thread (ROGUESQ_TSAN_UCODE=ON to instrument)")
    endif()
endif()

# s7467 class DW: same exemption for the ASan+UBSan arm (tools/build_asan.sh). The ucode touches only DMEM (masked) and guest
# RDRAM (one big host map, so ASan cannot see guest-side overruns anyway); instrumenting it only slows the gfx thread.
# ROGUESQ_ASAN_UCODE=ON instruments it (tools/build_asan.sh UCODE=1, its default since s7468: no flight cost, 0 ucode reports).
if (CMAKE_CXX_FLAGS_DEBUG MATCHES "fsanitize=address" OR CMAKE_CXX_FLAGS MATCHES "fsanitize=address")
    option(ROGUESQ_ASAN_UCODE "Instrument the RSP ucode TUs under ASan/UBSan" OFF)
    if (NOT ROGUESQ_ASAN_UCODE)
        set_property(SOURCE ${FACTOR5_UCODE_C} ${FACTOR5_UCODE_B_C} ${FACTOR5_BOOT_C} ${FACTOR5_UCODE_TLS_CPP}
            ${FACTOR5_UCODE_LEAN_CPP} ${FACTOR5_UCODE_NMAC_CPP} APPEND PROPERTY COMPILE_OPTIONS -fno-sanitize=address,undefined)
        message(STATUS "s7467: RSP ucode TUs built without -fsanitize=address,undefined (ROGUESQ_ASAN_UCODE=ON to instrument)")
    endif()
endif()

add_executable(RogueSquadron64Recomp
    ${CMAKE_SOURCE_DIR}/src/main/main.cpp
    $<$<PLATFORM_ID:Darwin>:${CMAKE_SOURCE_DIR}/src/main/rs64_display_mac.mm>
    $<$<PLATFORM_ID:Darwin>:${CMAKE_SOURCE_DIR}/src/main/rs64_controls_panel.cpp>
    $<$<PLATFORM_ID:Darwin>:${CMAKE_SOURCE_DIR}/src/main/rs64_imgui_metal.mm>
    $<$<PLATFORM_ID:Darwin>:${CMAKE_SOURCE_DIR}/lib/rt64/src/contrib/imgui/backends/imgui_impl_metal.mm>
    ${CMAKE_SOURCE_DIR}/src/main/rt64_render_context.cpp
    $<$<PLATFORM_ID:Darwin>:${CMAKE_SOURCE_DIR}/src/main/rs64_env_cache.cpp>
    ${CMAKE_SOURCE_DIR}/src/main/register_overlays.cpp
    ${CMAKE_SOURCE_DIR}/src/main/rs64_selfbranch.cpp
    ${CMAKE_SOURCE_DIR}/src/main/rs64_standins.cpp
    ${CMAKE_SOURCE_DIR}/src/main/rs64_settings.cpp
    ${CMAKE_SOURCE_DIR}/src/main/upstream_compat.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/aspMain.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/dpc_bridge.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7094_dma_shape.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7324_rcp_spill.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7702_fbread.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7331_reset_writer.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7095_dpc_model.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7096_fwd_cover.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7097_edit_census.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7389_fbld.cpp
    ${CMAKE_SOURCE_DIR}/src/main/s7391_spwm.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7521_ucode_watch.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7644_rspdma.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7523_slow_rdp.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7526_v2p_twin.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7535_ga_chk.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7106_rsptri.cpp
    ${CMAKE_SOURCE_DIR}/src/rsp/s7751_task_snap.cpp
    ${FACTOR5_UCODE_TLS_CPP}
    ${FACTOR5_UCODE_LEAN_CPP}
    ${FACTOR5_UCODE_NMAC_CPP}
    ${FACTOR5_BOOT_C}
    ${FACTOR5_UCODE_C}
    ${FACTOR5_UCODE_B_C}
    $<$<PLATFORM_ID:Windows>:${CMAKE_SOURCE_DIR}/src/main/app.rc>
)

# s7447 class DD: route the hand-written src/main + src/rsp fprintf/std::fprintf sites through rs64_diag_fprintf so
# ROGUESQ_DIAG_QUIET=1 drops them too (default output unchanged). The ucode .cpp arms keep RS64_UCODE_FLAGS.
option(RS64_DIAG_ROUTE "Force-include include/rs64_diag_route.h into src/main + src/rsp host sources" ON)
if (RS64_DIAG_ROUTE AND NOT MSVC)
    file(GLOB RS64_DIAG_ROUTE_SRC ${CMAKE_SOURCE_DIR}/src/main/*.cpp ${CMAKE_SOURCE_DIR}/src/rsp/*.cpp)
    list(FILTER RS64_DIAG_ROUTE_SRC EXCLUDE REGEX "factor5_ucode")
    set_property(SOURCE ${RS64_DIAG_ROUTE_SRC} APPEND PROPERTY COMPILE_OPTIONS
        "-include;${CMAKE_SOURCE_DIR}/include/rs64_diag_route.h")
    # lib targets linked only into this executable (rs64_diag_fprintf resolves at link); no lib/ source edits.
    foreach(t rt64 librecomp ultramodern)
        if (TARGET ${t})
            target_compile_options(${t} PRIVATE
                "$<$<COMPILE_LANGUAGE:CXX>:SHELL:-include ${CMAKE_SOURCE_DIR}/include/rs64_diag_route.h>")
        endif()
    endforeach()
endif()

target_include_directories(RogueSquadron64Recomp PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${RECOMP_FUNCS_DIR}
    ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/N64Recomp/include
    ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/ultramodern/include
    ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/librecomp/include
    ${CMAKE_SOURCE_DIR}/lib/rt64/src
    ${CMAKE_SOURCE_DIR}/lib/rt64/src/contrib
    ${CMAKE_SOURCE_DIR}/lib/rt64/src/contrib/hlslpp/include
)

# s7620 G6b step 3: F6 Controls panel. Reads plume's Metal objects (metal-cpp headers) and draws with ImGui's Metal backend.
if (APPLE)
    set_source_files_properties(${CMAKE_SOURCE_DIR}/src/main/rs64_controls_panel.cpp PROPERTIES INCLUDE_DIRECTORIES
        "${CMAKE_SOURCE_DIR}/lib/rt64/src/contrib/plume;${CMAKE_SOURCE_DIR}/lib/rt64/src/contrib/plume/contrib/metal-cpp")
    set_source_files_properties(${CMAKE_SOURCE_DIR}/src/main/rs64_imgui_metal.mm
        ${CMAKE_SOURCE_DIR}/lib/rt64/src/contrib/imgui/backends/imgui_impl_metal.mm PROPERTIES
        COMPILE_OPTIONS "-fobjc-arc" INCLUDE_DIRECTORIES "${CMAKE_SOURCE_DIR}/lib/rt64/src/contrib/imgui")
endif()

if (NOT MSVC)
    target_compile_options(RogueSquadron64Recomp PRIVATE
        -fno-strict-aliasing
        -fms-extensions
    )
endif()

# s6699: the rest of the host code (src/main, src/rsp, librecomp, ultramodern) and the recompiled
# guest were -O0 under the Debug config. ON by default since s6700 (qualified: lvl1/7/10 + hangar route 300 s clean).
option(ROGUESQ_SRC_OPT "Compile host code (src/, librecomp, ultramodern) with -O2 under Debug" ON)
option(ROGUESQ_FUNCS_OPT "Compile RecompiledFuncs + PatchesLib with -O2 under Debug" ON)
if (ROGUESQ_SRC_OPT AND NOT MSVC)
    target_compile_options(RogueSquadron64Recomp PRIVATE -O2)
    target_compile_options(librecomp PRIVATE -O2)
    target_compile_options(ultramodern PRIVATE -O2)
endif()
if (ROGUESQ_FUNCS_OPT AND NOT MSVC)
    target_compile_options(RecompiledFuncs PRIVATE -O2)
    if (TARGET PatchesLib)
        target_compile_options(PatchesLib PRIVATE -O2)
    endif()
endif()

if (MSVC)
    target_link_options(RogueSquadron64Recomp PRIVATE /OPT:NOICF)
    # /FORCE:MULTIPLE lets PatchesLib's overrides win against the same-named
    # auto-generated functions in RecompiledFuncs. lld-link processes libs in
    # command-line order and takes the first definition; for our symbols
    # PatchesLib comes first in the link line. Without this flag the linker
    # treats the second definition as a fatal error. The risk: any genuinely
    # accidental duplicate elsewhere is masked. If that becomes a problem we
    # can switch to /FORCE:MULTIPLE only on the patched-symbol set via a
    # per-symbol .def or by carving out the patched .obj from RecompiledFuncs.
    target_link_options(RogueSquadron64Recomp PRIVATE /FORCE:MULTIPLE)
endif()

# ---- SDL2 (Windows: fetch; Linux/Mac: find_package) ----
if (WIN32)
    include(FetchContent)
    if (DEFINED ENV{SDL2_VERSION})
        set(SDL2_VERSION $ENV{SDL2_VERSION})
    else()
        set(SDL2_VERSION "2.30.3")
    endif()
    FetchContent_Declare(sdl2
        URL https://github.com/libsdl-org/SDL/releases/download/release-${SDL2_VERSION}/SDL2-devel-${SDL2_VERSION}-VC.zip
    )
    FetchContent_MakeAvailable(sdl2)
    target_include_directories(RogueSquadron64Recomp PRIVATE ${sdl2_SOURCE_DIR}/include)
    target_link_directories(RogueSquadron64Recomp PRIVATE ${sdl2_SOURCE_DIR}/lib/x64)
    add_custom_command(TARGET RogueSquadron64Recomp POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${sdl2_SOURCE_DIR}/lib/x64/SDL2.dll"
            "${CMAKE_SOURCE_DIR}/lib/rt64/src/contrib/dxc/bin/x64/dxil.dll"
            "${CMAKE_SOURCE_DIR}/lib/rt64/src/contrib/dxc/bin/x64/dxcompiler.dll"
            $<TARGET_FILE_DIR:RogueSquadron64Recomp>)
    set_target_properties(RogueSquadron64Recomp PROPERTIES
        LINK_FLAGS_DEBUG          "/SUBSYSTEM:CONSOLE"
        LINK_FLAGS_RELEASE        "/SUBSYSTEM:WINDOWS /ENTRY:mainCRTStartup"
        LINK_FLAGS_RELWITHDEBINFO "/SUBSYSTEM:WINDOWS /ENTRY:mainCRTStartup"
    )
    target_link_libraries(RogueSquadron64Recomp PRIVATE SDL2 Winmm.lib)
elseif (APPLE)
    find_package(SDL2 REQUIRED)
    find_package(Threads REQUIRED)
    target_include_directories(RogueSquadron64Recomp PRIVATE ${SDL2_INCLUDE_DIRS})
    target_link_libraries(RogueSquadron64Recomp PRIVATE ${CMAKE_DL_LIBS} Threads::Threads SDL2::SDL2)
else()
    find_package(SDL2 REQUIRED)
    find_package(Threads REQUIRED)
    target_include_directories(RogueSquadron64Recomp PRIVATE ${SDL2_INCLUDE_DIRS})
    target_link_libraries(RogueSquadron64Recomp PRIVATE SDL2::SDL2 ${CMAKE_DL_LIBS} Threads::Threads)
endif()

# PatchesLib must come BEFORE RecompiledFuncs so the linker takes its
# overrides for any duplicated symbol names (Zelda's pattern).
if (PATCHES_BUILD_OK)
    target_link_libraries(RogueSquadron64Recomp PRIVATE PatchesLib)
    if (APPLE)
        # ld64 pulls archive members lazily, so a patch overriding an already
        # defined (weak, tools/weaken_patched_funcs.py) symbol is never linked.
        target_link_options(RogueSquadron64Recomp PRIVATE
           "LINKER:-force_load,$<TARGET_FILE:PatchesLib>")
    endif()
endif()

target_link_libraries(RogueSquadron64Recomp PRIVATE
    RecompiledFuncs
    librecomp
    ultramodern
    rt64
)

set_property(TARGET RogueSquadron64Recomp PROPERTY VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
