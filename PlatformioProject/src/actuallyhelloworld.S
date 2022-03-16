.cpu cortex-m0
.align 2

.data

LIT0: .asciz "een"
LIT1: .asciz "twee"
LIT2: .asciz "drie"

.text
.global youriMain

youriMain:
push { r1, r2, r3, r4, r5, r6, r7, lr }
mov r1, #2
mov r2, #4
mov r3, #5
mul r1, r1, r1
mul r2, r3, r2
sub r2, r1, r2
add r3, r1, r3
mov r4, #2
mul r1, r4, r1
mov r5, #4
add r1, r5, r1
mov r0, r1
bl printlnInteger
ldr r0, =LIT0
bl printlnStr
ldr r0, =LIT1
bl printlnStr
ldr r0, =LIT2
bl printlnStr
mov r0, #4
bl printlnInteger
pop { r1, r2, r3, r4, r5, r6, r7, pc }
