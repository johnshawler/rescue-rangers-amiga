.section .entry,"ax"
.globl _start
_start:
 lea dp_stack_end(%pc),%sp
 bra.w experimental_direct_paula_main
.section .bss
.balign 4
dp_stack:
 .space 2048
dp_stack_end:
