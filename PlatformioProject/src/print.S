.cpu cortex-m0
.align 2

.text
.global print

print:
push { r4, lr }
mov r4, r0
ldr r1, =65535
cmp r0, r1
mov r0, r4
bls printlnInteger
bhi printlnStr
pop { r4, pc }
