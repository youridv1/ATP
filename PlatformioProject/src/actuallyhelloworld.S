.cpu cortex-m0
.align 2

.data

LIT0: .asciz "what"

.text
.global youriMain

youriMain:
push { r4, r5, lr }
mov r4, #4
mov r0, r4
bl printlnInteger
whileBegin_5cfbee63bd:
mov r1, r4
mov r0, #0
cmp r0, r1
beq whileEnd_5cfbee63bd
mov r5, #1
sub r4, r4, r5
ldr r0, =LIT0
bl printlnStr
mov r0, r4
bl printlnInteger
b whileBegin_5cfbee63bd
whileEnd_5cfbee63bd:
pop { r4, r5, pc }
