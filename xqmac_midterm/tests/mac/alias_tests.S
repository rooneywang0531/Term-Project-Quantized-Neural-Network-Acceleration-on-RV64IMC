.section .text.alias,"ax",@progbits
.balign 2
.globl alias_ss_rd_a
.type alias_ss_rd_a,@function
alias_ss_rd_a:
    .insn r4 0x0b, 0, 0, a0, a0, a1, a2
    mv a0, a0
    ret
.size alias_ss_rd_a, .-alias_ss_rd_a
.balign 2
.globl alias_ss_rd_w
.type alias_ss_rd_w,@function
alias_ss_rd_w:
    .insn r4 0x0b, 0, 0, a1, a0, a1, a2
    mv a0, a1
    ret
.size alias_ss_rd_w, .-alias_ss_rd_w
.balign 2
.globl alias_ss_rd_acc
.type alias_ss_rd_acc,@function
alias_ss_rd_acc:
    .insn r4 0x0b, 0, 0, a2, a0, a1, a2
    mv a0, a2
    ret
.size alias_ss_rd_acc, .-alias_ss_rd_acc
.balign 2
.globl alias_ss_a_w
.type alias_ss_a_w,@function
alias_ss_a_w:
    .insn r4 0x0b, 0, 0, t0, a0, a0, a2
    mv a0, t0
    ret
.size alias_ss_a_w, .-alias_ss_a_w
.balign 2
.globl alias_ss_acc_a
.type alias_ss_acc_a,@function
alias_ss_acc_a:
    .insn r4 0x0b, 0, 0, t0, a0, a1, a0
    mv a0, t0
    ret
.size alias_ss_acc_a, .-alias_ss_acc_a
.balign 2
.globl alias_ss_acc_w
.type alias_ss_acc_w,@function
alias_ss_acc_w:
    .insn r4 0x0b, 0, 0, t0, a0, a1, a1
    mv a0, t0
    ret
.size alias_ss_acc_w, .-alias_ss_acc_w
.balign 2
.globl alias_ss_all_a
.type alias_ss_all_a,@function
alias_ss_all_a:
    .insn r4 0x0b, 0, 0, a0, a0, a0, a0
    mv a0, a0
    ret
.size alias_ss_all_a, .-alias_ss_all_a
.balign 2
.globl alias_ss_rd_zero
.type alias_ss_rd_zero,@function
alias_ss_rd_zero:
    .insn r4 0x0b, 0, 0, zero, a0, a1, a2
    mv a0, zero
    ret
.size alias_ss_rd_zero, .-alias_ss_rd_zero
.balign 2
.globl alias_ss_all_zero
.type alias_ss_all_zero,@function
alias_ss_all_zero:
    .insn r4 0x0b, 0, 0, a0, zero, zero, zero
    mv a0, a0
    ret
.size alias_ss_all_zero, .-alias_ss_all_zero
.balign 2
.globl alias_ss_rd_separate
.type alias_ss_rd_separate,@function
alias_ss_rd_separate:
    .insn r4 0x0b, 0, 0, t0, a0, a1, a2
    mv a0, t0
    ret
.size alias_ss_rd_separate, .-alias_ss_rd_separate
.balign 2
.globl alias_ss_a_zero
.type alias_ss_a_zero,@function
alias_ss_a_zero:
    .insn r4 0x0b, 0, 0, a0, zero, a1, a2
    mv a0, a0
    ret
.size alias_ss_a_zero, .-alias_ss_a_zero
.balign 2
.globl alias_ss_w_zero
.type alias_ss_w_zero,@function
alias_ss_w_zero:
    .insn r4 0x0b, 0, 0, a0, a0, zero, a2
    mv a0, a0
    ret
.size alias_ss_w_zero, .-alias_ss_w_zero
.balign 2
.globl alias_ss_acc_zero
.type alias_ss_acc_zero,@function
alias_ss_acc_zero:
    .insn r4 0x0b, 0, 0, a0, a0, a1, zero
    mv a0, a0
    ret
.size alias_ss_acc_zero, .-alias_ss_acc_zero
.balign 2
.globl alias_us_rd_a
.type alias_us_rd_a,@function
alias_us_rd_a:
    .insn r4 0x0b, 1, 0, a0, a0, a1, a2
    mv a0, a0
    ret
.size alias_us_rd_a, .-alias_us_rd_a
.balign 2
.globl alias_us_rd_w
.type alias_us_rd_w,@function
alias_us_rd_w:
    .insn r4 0x0b, 1, 0, a1, a0, a1, a2
    mv a0, a1
    ret
.size alias_us_rd_w, .-alias_us_rd_w
.balign 2
.globl alias_us_rd_acc
.type alias_us_rd_acc,@function
alias_us_rd_acc:
    .insn r4 0x0b, 1, 0, a2, a0, a1, a2
    mv a0, a2
    ret
.size alias_us_rd_acc, .-alias_us_rd_acc
.balign 2
.globl alias_us_a_w
.type alias_us_a_w,@function
alias_us_a_w:
    .insn r4 0x0b, 1, 0, t0, a0, a0, a2
    mv a0, t0
    ret
.size alias_us_a_w, .-alias_us_a_w
.balign 2
.globl alias_us_acc_a
.type alias_us_acc_a,@function
alias_us_acc_a:
    .insn r4 0x0b, 1, 0, t0, a0, a1, a0
    mv a0, t0
    ret
.size alias_us_acc_a, .-alias_us_acc_a
.balign 2
.globl alias_us_acc_w
.type alias_us_acc_w,@function
alias_us_acc_w:
    .insn r4 0x0b, 1, 0, t0, a0, a1, a1
    mv a0, t0
    ret
.size alias_us_acc_w, .-alias_us_acc_w
.balign 2
.globl alias_us_all_a
.type alias_us_all_a,@function
alias_us_all_a:
    .insn r4 0x0b, 1, 0, a0, a0, a0, a0
    mv a0, a0
    ret
.size alias_us_all_a, .-alias_us_all_a
.balign 2
.globl alias_us_rd_zero
.type alias_us_rd_zero,@function
alias_us_rd_zero:
    .insn r4 0x0b, 1, 0, zero, a0, a1, a2
    mv a0, zero
    ret
.size alias_us_rd_zero, .-alias_us_rd_zero
.balign 2
.globl alias_us_all_zero
.type alias_us_all_zero,@function
alias_us_all_zero:
    .insn r4 0x0b, 1, 0, a0, zero, zero, zero
    mv a0, a0
    ret
.size alias_us_all_zero, .-alias_us_all_zero
.balign 2
.globl alias_us_rd_separate
.type alias_us_rd_separate,@function
alias_us_rd_separate:
    .insn r4 0x0b, 1, 0, t0, a0, a1, a2
    mv a0, t0
    ret
.size alias_us_rd_separate, .-alias_us_rd_separate
.balign 2
.globl alias_us_a_zero
.type alias_us_a_zero,@function
alias_us_a_zero:
    .insn r4 0x0b, 1, 0, a0, zero, a1, a2
    mv a0, a0
    ret
.size alias_us_a_zero, .-alias_us_a_zero
.balign 2
.globl alias_us_w_zero
.type alias_us_w_zero,@function
alias_us_w_zero:
    .insn r4 0x0b, 1, 0, a0, a0, zero, a2
    mv a0, a0
    ret
.size alias_us_w_zero, .-alias_us_w_zero
.balign 2
.globl alias_us_acc_zero
.type alias_us_acc_zero,@function
alias_us_acc_zero:
    .insn r4 0x0b, 1, 0, a0, a0, a1, zero
    mv a0, a0
    ret
.size alias_us_acc_zero, .-alias_us_acc_zero
.section .note.GNU-stack,"",@progbits
