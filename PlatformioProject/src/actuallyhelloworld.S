.cpu cortex-m0
.align 2
.data
.text
.global youriMain
youriMain:
push { r1, r2, r3, r4, lr }
mov r1, #2
mov r2, #4
mov r3, #5
mul r1, r1, r1
mul r2, r3, r2
sub r2, r1, r2
add r3, r1, r3
mov r4, #2
mul r1, r4, r1
mov r0, r1
bl printlnInteger
pop { r1, r2, r3, r4, pc }