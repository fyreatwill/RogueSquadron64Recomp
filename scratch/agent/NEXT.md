# Next work unit: qualify the selected task/output contract against retail

HYPOTHESIS-ID: m5-task-output-contract-retail-parity

The M3 heap-span guard remains an open build dependency, not this iteration's
work unit. The local `build/N64Recomp` exists, but Apple Clang has no MIPS
target and no `mips64-elf-*` compiler/linker is present. Do not repeat that
tool check; resume M3 only after those inputs are supplied.

Run the existing qualified port recipe with task-contract/image-stage
controls, plus an independent retail oracle capture with whole-RDRAM and both
target-VI controls. Join the named contract `data_ptr=0x80171E70`,
`data_size=1` by task generation to `output_buff`/`output_buff_size` and the
retail task's output/writeback observations.

- H1: retail also has empty ABI output fields and a separate writeback edge;
  the selected port contract has parity.
- H2: retail publishes a nonempty output field or a task-generation-matched
  output destination; the port ABI/edge contract differs.
- H3: either arm lacks whole-RDRAM or both target-VI controls; the comparison
  is coverage-invalid and must be rerun.

Use `scratch/agent/run_s3840_m5_task_output_contract_edge.sh` for the port
recipe and the task-field watch options documented in
`tools/oracle/README.md`. Capture both arms in one iteration and use only
phase-gated rows. Do not add a writeback or output guard.

M3 follow-up after toolchain restoration:

    cmake -S . -B build -DMIPS_TOOLCHAIN_DIR=<valid-toolchain> \
      -DN64RECOMP_EXE=<valid-N64Recomp.exe>
    cmake --build build --config Debug --target PatchesLib
    rg -n "func_80007D74" RecompiledPatches/patches.c
