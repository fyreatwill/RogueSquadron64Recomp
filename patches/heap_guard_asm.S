.set noreorder
.set noat

.section .recomp_patch, "ax", @progbits
.align 2
.globl allocateDisplayListBuffer
.type allocateDisplayListBuffer, @function
allocateDisplayListBuffer:
    lui     $v1, 0x8011
    lw      $v1, 0x63B0($v1)
    addiu   $sp, $sp, -0x18
    bne     $v1, $zero, .L_de0
    sw      $ra, 0x10($sp)
    jal     findAndUnlinkSmallestEntry
    nop
    addu    $v1, $v0, $zero
    beq     $v1, $zero, .L_dd8
    nop
    lw      $v0, 0($v1)
    beq     $v0, $zero, .L_db8
    addu    $a0, $v1, $zero
.L_da8:
    lw      $a0, 0($a0)
    lw      $v0, 0($a0)
    bne     $v0, $zero, .L_da8
    nop
.L_db8:
    lui     $v0, 0x8011
    lw      $v0, 0x63B0($v0)
    beq     $v0, $zero, .L_dcc
    sw      $v0, 0($a0)
    sw      $a0, 4($v0)
.L_dcc:
    lui     $at, 0x8011
    sw      $v1, 0x63B0($at)
    sw      $zero, 4($v1)
.L_dd8:
    lui     $v1, 0x8011
    lw      $v1, 0x63B0($v1)
.L_de0:
    lui     $v0, 0x8011
    lw      $v0, 0x63B0($v0)
    lw      $v0, 0($v0)
    lui     $at, 0x8011
    sw      $v0, 0x63B0($at)
    bnel    $v0, $zero, .L_dfc
    sw      $zero, 4($v0)
.L_dfc:
    lui     $a1, 0x8011
    lw      $a1, 0x63FC($a1)
    lw      $v0, 0($a1)
    bne     $v0, $zero, .L_e18
    addu    $a0, $v1, $zero
    j       .L_e30
    sw      $a0, 0($a1)
.L_e18:
    lui     $v0, 0x8012
    lw      $v0, -0x5824($v0)
    lw      $v1, 0($v0)
    sw      $a0, 0($v1)
    lw      $v0, 0($v0)
    sw      $v0, 4($a0)
.L_e30:
    lui     $v1, 0x8012
    lw      $v1, -0x5824($v1)
    sw      $zero, 0($a0)
    sw      $a0, 0($v1)
    addiu   $v1, $a0, 0x100
    lui     $at, 0x8011
    sw      $v1, 0x63D4($at)
    lw      $ra, 0x10($sp)
    addiu   $v0, $a0, 8
    jr      $ra
    addiu   $sp, $sp, 0x18
.size allocateDisplayListBuffer, .-allocateDisplayListBuffer
