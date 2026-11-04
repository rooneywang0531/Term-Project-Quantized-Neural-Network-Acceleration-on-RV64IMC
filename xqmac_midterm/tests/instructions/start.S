.section .text.init
.globl _start
_start:
    la sp, __stack_top
    la t0, __bss_start
    la t1, __bss_end
1:
    bgeu t0, t1, 2f
    sd zero, 0(t0)
    addi t0, t0, 8
    j 1b
2:
    call main
    slli a0, a0, 1
    ori a0, a0, 1
    la t0, tohost
    sd a0, 0(t0)
3:
    j 3b

.section .tohost, "aw", @progbits
.balign 64
.globl tohost
tohost:
    .dword 0
.balign 64
.globl fromhost
fromhost:
    .dword 0
