import sys
import time
import os
from chips import Memory, CPU, ROM32K, Register, PC, Bit, Bus, CPUFast
from debug_functions import padded_binary, getCurrentKeyName, getKeyCode
import pygame
import math

# make this true to use a faster CPU, but one that is less accurate to real life. kinda buggy
useFast = False
runtime = time.time()
# Setting up input and output pins
print('Initializing starting circuits')
s_time = time.time()
if not useFast:
    inM = Bus()
    instruction = Bus()
    reset = Bit()
    outM = Bus()
    writeM = Bit()
    addressM = Bus()

    AReg = Register()
    DReg = Register()
    programCounter = PC()
    pcAddress = Bus()

    memory = Memory()
    rom = ROM32K()
else:
    memory = []
    for i in range(24577):
        bus = []
        for j in range(16):
            bus.append(False)
        # keeps track of whether theres a 1 in the bus. bus[16]
        bus.append(False)
        memory.append(bus)
    bus = []
    for i in range(17):
        bus.append(False)
    inM = bus[:]
    instruction = bus[:]
    reset = [False]
    outM = bus[:]
    writeM = [False]
    addressM = bus[:]

    AReg = bus[:]
    DReg = bus[:]
    programCounter = [0]
    pcAddress = [0]

    rom = []
e_time = time.time()

print(f'Completed in {e_time - s_time} seconds')

# reading in the instructions-------------------------------------------------------------------------------------------
fileToRead = input('Enter name of file')
fileToRead = os.path.join(sys.path[0], f'Machine Languange Programs/{fileToRead}')

instructions = []
lines = []
with open(fileToRead, 'r') as f:
    lines = f.readlines()

for line in lines:
    line = line.replace('\n', '')
    instructions.append(line)

counter = 0
if not useFast:
    for i in instructions:
        rom.ram[counter] = Bus(i)
        counter += 1
else:
    for i in instructions:
        rom.append(i[::-1])
# ----------------------------------------------------------------------------------------------------------------------

# setting up pygame ----------------------------------------------------------------------------------------------------
width = 1280
height = 720
borderWidth = 20

disp = pygame.display.set_mode((width, height))
pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (136, 136, 136)
LIGHTGREEN = (102, 255, 255)

INPUTBOX = (200, 200, 200)
INPUTBOXACTIVE = (240, 240, 240)

font = pygame.font.SysFont('unispace', 40)
text = font.render('Enter memory address in decimal', True, BLACK)

input_box = pygame.Rect(40, 80, 456, 30)
input_text = ''
input_box_text = font.render(input_text, True, BLACK)

CPUSpeedBox = pygame.Rect(1235, 310, 40, 30)

memoryValues = []

active = False
input_active = False
run = True
runEmulator = False
emulatorSpeed = 0.0
e_SpeedStr = '0.0'
CPUSpeedInputActive = False


# -----------------------------------------------------------------------------------------------------------------------
def getValuesNearMemAddress(s: str):
    index = int(s)
    vals = []
    if not useFast:
        if 16383 < index < 24576:
            index -= 16384
            for i in range(index - 6, index + 6):
                try:
                    vals.append(f'[{i + 16384}]:     {memory.screen.memory[i]}')
                except IndexError:
                    continue
        elif index == 24576:
            index = 0
            vals.append(f'[24576]:      {memory.keyboard.state}')
        else:
            for i in range(index - 6, index + 6):
                try:
                    if i >= 0:
                        vals.append(f'[{i}]:    {memory.mem.ram[i]}')
                except IndexError:
                    continue
    else:
        for i in range(index - 6, index + 6):
            try:
                if i >= 0:
                    s = ''.join([str(int(j)) for j in memory[i][::-1][1:]])
                    vals.append(f'[{i}]:    ' + s)
            except IndexError:
                continue

    return vals


def setMemoryAddress(memory, addr: int, value: int, useFast: bool):
    if not useFast:
        memory.mem.ram[addr] = Bus(padded_binary(value))
    else:
        s = padded_binary(value)
        oneExists = False
        if '1' in s:
            oneExists = True
        b = [True if i == '1' else False for i in s[::-1]]
        b.append(oneExists)
        memory[addr] = b[:]


def drawPixel(x, y):
    pygame.draw.rect(disp, BLACK, (x, y, 1, 1))


print('Starting game loop')
run = True
debug = False
setMemoryAddress(memory, addr=0, value=64, useFast=useFast)
while run:
    # graphics ---------------------------------------------------------------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = True
            else:
                active = False
            if math.hypot(612 - event.pos[0], 140 - event.pos[1]) <= 70:
                runEmulator = not runEmulator
            if CPUSpeedBox.collidepoint(event.pos):
                CPUSpeedInputActive = True
            else:
                CPUSpeedInputActive = False
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    active = False
                    memoryValues = getValuesNearMemAddress(input_text)
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
            if CPUSpeedInputActive:
                if event.key == pygame.K_RETURN:
                    CPUSpeedInputActive = False
                    emulatorSpeed = float(e_SpeedStr)
                elif event.key == pygame.K_BACKSPACE:
                    e_SpeedStr = e_SpeedStr[:-1]
                else:
                    e_SpeedStr += event.unicode

    disp.fill(WHITE)
    # drawing border----------------------------------------------------------------------------------------------------
    pygame.draw.rect(disp, GRAY, (width - 512 - borderWidth * 2, 0, 512 + borderWidth * 2, borderWidth))
    pygame.draw.rect(disp, GRAY, (width - 512 - borderWidth * 2, borderWidth, borderWidth, 256 + borderWidth))
    pygame.draw.rect(disp, GRAY, (width - 512 - borderWidth * 2, 256 + borderWidth, 512 + borderWidth * 2, borderWidth))
    pygame.draw.rect(disp, GRAY, (width - borderWidth, borderWidth, borderWidth, 256))
    # ------------------------------------------------------------------------------------------------------------------

    # drawing memory boxes ---------------------------------------------------------------------------------------------
    if not active and len(input_text) > 0:
        memoryValues = getValuesNearMemAddress(input_text)
    for i in range(len(memoryValues)):
        pygame.draw.rect(disp, LIGHTGREEN, (40, 120 + 30 * i + 10 * i, 456, 30))
        disp.blit(font.render(memoryValues[i], True, BLACK), (40, 120 + 30 * i + 10 * i))

    if active:
        pygame.draw.rect(disp, INPUTBOXACTIVE, input_box)
    else:
        pygame.draw.rect(disp, INPUTBOX, input_box)

    disp.blit(text, (40, 40))
    input_box_text = font.render(input_text, True, BLACK)
    disp.blit(input_box_text, (40, 80))

    # ------------------------------------------------------------------------------------------------------------------

    # drawing play button ----------------------------------------------------------------------------------------------
    pygame.draw.circle(disp, BLACK, (612, 140), 75)
    pygame.draw.circle(disp, (221, 220, 198), (612, 140), 70)
    if not runEmulator:
        p1 = (582, 90)
        p2 = (582, 190)
        p3 = (662, 140)
        line_color = (189, 100, 55)
        pygame.draw.polygon(disp, (50, 227, 55), [p1, p2, p3])
        pygame.draw.line(disp, line_color, p1, p2, 5)
        pygame.draw.line(disp, line_color, p2, p3, 5)
        pygame.draw.line(disp, line_color, p3, p1, 5)
    else:
        pygame.draw.rect(disp, (200, 100, 55), (582, 90, 20, 100), border_radius=5)
        pygame.draw.rect(disp, (200, 100, 55), (618, 90, 20, 100), border_radius=5)
    # ------------------------------------------------------------------------------------------------------------------

    # drawing cpu speed changing box------------------------------------------------------------------------------------
    if not CPUSpeedInputActive:
        pygame.draw.rect(disp, INPUTBOX, CPUSpeedBox)
    else:
        pygame.draw.rect(disp, INPUTBOXACTIVE, CPUSpeedBox)
    disp.blit(font.render('Delay between CPU Cycles(seconds):', True, BLACK), (725, 310))
    disp.blit(font.render(e_SpeedStr, True, BLACK), (1235, 310))
    # ------------------------------------------------------------------------------------------------------------------

    # rendering the screen by reading the screen memory map
    if not useFast:
        for i in range(256):
            for j in range(512):
                bus = memory.screen.memory[i * 32 + j // 16]
                if bus.oneExists:
                    for k in range(16):
                        if bus[k]:
                            drawPixel(748 + j + k, 20 + i)
    else:
        for i in range(256):
            for j in range(32):
                index = j + 32 * i + 16384
                if memory[j + 32 * i + 16384][16]:
                    for k in range(16):
                        if memory[index][k]:
                            drawPixel(748 + 16 * j + k, 20 + i)

    disp.blit(font.render('Current Instruction:', True, BLACK), (725, 350))
    pygame.draw.rect(disp, LIGHTGREEN, (725, 390, len(str(instruction)) * 16, 30))
    if not useFast:
        disp.blit(font.render(str(instruction), True, BLACK), (728, 393))
    else:
        try:
            p = rom[pcAddress[0]][::-1]
        except IndexError:
            p = 'End of file'

        disp.blit(font.render(p, True, BLACK), (728, 393))

    disp.blit(font.render('Program Counter:', True, BLACK), (725, 434))
    if not useFast:
        pc = str(programCounter.state)
        pc = pc[pc.index('(') + 1:pc.index(')')]
    else:
        pc = str(pcAddress[0])
    pygame.draw.rect(disp, LIGHTGREEN, (725, 474, len(pc) * 16, 30))
    disp.blit(font.render(pc, True, BLACK), (728, 479))
    pygame.display.update()
    # -------------------------------------------------------------------------------------------------------------------

    if runEmulator:
        if not useFast:
            # setting the currently pressed key into the keyboard memory location
            keyPressed = getKeyCode(getCurrentKeyName(pygame.key.get_pressed()))
            memory.keyboard.setState(keyPressed)

            memory.input(inBus=outM, load=writeM, address=addressM)
            memory.output(output=inM, address=addressM)

            rom.getItemAtLocation(address=pcAddress, output=instruction)

            CPU(inM=inM, instruction=instruction, reset=reset, outM=outM, writeM=writeM, addressM=addressM,
                pcAddress=pcAddress,
                ARegister=AReg, DRegister=DReg, programCounter=programCounter)

        else:
            keyPressed = getKeyCode(getCurrentKeyName(pygame.key.get_pressed()))
            memory[-1] = [True if i == '1' else False for i in keyPressed[::-1]]

            addr = ''.join([str(int(i)) for i in addressM[::-1][1:]])
            if writeM[0]:
                memory[int(addr, 2)] = outM[:]
            inM = memory[int(addr, 2)][:]

            try:
                instruction = rom[pcAddress[0]]
            except IndexError:
                instruction = [False] * 16

            CPUFast(inM, instruction, reset, outM, writeM, addressM, pcAddress, AReg, DReg)
    time.sleep(emulatorSpeed)

print(f'Runtime: {time.time() - runtime}')
