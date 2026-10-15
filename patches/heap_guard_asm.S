.set noreorder
.set noat

.section .recomp_patch, "ax", @progbits
.align 2
.globl allocateDisplayListBuffer
.type allocateDisplayListBuffer, @function
allocateDisplayListBuffer:
    lui     $t0, 0x8011
    lw      $t0, 0x63B0($t0)
    bnez    $t0, 1f
    nop
    lui     $t9, 0x8002
    ori     $t9, $t9, 0x221C
    jalr    $t9
    nop
    addu    $t0, $v0, $zero
1:
    beq     $t0, $zero, 2f
    nop
    addiu   $v0, $t0, 8
    jr      $ra
    nop
2:
    addu    $v0, $zero, $zero
    jr      $ra
    nop
.size allocateDisplayListBuffer, .-allocateDisplayListBuffer
