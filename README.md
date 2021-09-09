# Python Computer Simulator
 A fully programmable computer in Python

Features an RISC 16 bit CPU based on the Harvard architecture, 16K RAM (2^14 16-bit words), 32K of read-only 
instruction memory (2^15 16-bit words), a 512x256 screen with its own dedicated memory, and keyboard input.

Inspired by the HACK computer (https://www.nand2tetris.org/), and uses its instruction set and assembly language.

Use the included assembler to write your own programs and execute them.

Programs included: (which can also be found at https://www.nand2tetris.org/software)\n
Add.hack- Computes 2+3, and stores it in RAM[0].\n
mult.hack- Computes the product of RAM[0] and RAM[1] and stores it in RAM[3].\n
Rect.hack- Draws a 16(width)xRAM[0](height) rectangle.\n
test.hack- Computes 10 + 20 + 100, and stores it in RAM[0,1,2].\n

