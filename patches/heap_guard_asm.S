.set noreorder
.set noat

.section .recomp_patch, "ax", @progbits
.align 2
.globl allocateDisplayListBuffer
.type allocateDisplayListBuffer, @function
allocateDisplayListBuffer:
    lui     $t3, 0x8011
    lw      $t0, 0x63B0($t3)
    bnez    $t0, 1f
    nop
    lui     $t9, 0x8002
    ori     $t9, $t9, 0x221C
    jalr    $t9
    nop
    addu    $t0, $v0, $zero
    beq     $t0, $zero, 2f
    nop
    addu    $t1, $t0, $zero
3:
    lw      $t2, 0($t1)
    beq     $t2, $zero, 4f
    nop
    addu    $t1, $t2, $zero
    b       3b
    nop
4:
    sw      $t0, 0x63B0($t3)
    sw      $zero, 4($t0)
1:
    lw      $t0, 0x63B0($t3)
    beq     $t0, $zero, 2f
    nop
    lw      $t1, 0($t0)
    sw      $t1, 0x63B0($t3)
    beq     $t1, $zero, 5f
    nop
    sw      $zero, 4($t1)
5:
    lui     $t4, 0x8011
    ori     $t4, $t4, 0xA7DC
    lw      $t4, 0($t4)
    lw      $t4, 0($t4)
    lw      $t5, 0x63FC($t3)
    lw      $t6, 0($t5)
    beq     $t6, $zero, 6f
    nop
    lw      $t7, 0($t4)
    sw      $t0, 0($t7)
    sw      $t7, 4($t0)
    b       7f
    nop
6:
    sw      $t0, 0($t5)
7:
    sw      $zero, 0($t0)
    addiu   $t1, $t0, 0x100
    sw      $t1, 0x63D4($t3)
    addiu   $v0, $t0, 8
    jr      $ra
    nop
2:
    addu    $v0, $zero, $zero
    jr      $ra
    nop
.size allocateDisplayListBuffer, .-allocateDisplayListBuffer
