import sys
import time
import os

o_fileName = input("Enter Name")
fileName = os.path.join(sys.path[0], f'Assembly Programs/{o_fileName}')
symbolTable = {}

# initializing symbolTable
for i in range(16):
    symbolTable[f"R{i}"] = i
symbolTable['SCREEN'] = 16384
symbolTable['KBD'] = 24576
symbolTable['SP'] = 0
symbolTable['LCL'] = 1
symbolTable['ARG'] = 2
symbolTable['THIS'] = 3
symbolTable['THAT'] = 4

compTable = {'0': '101010', '1': '111111', '-1': '111010', 'D': '001100', 'X': '110000', '!D': '001101', '!X': '110001',
             '-D': '001111', '-X': '110011', 'D+1': '011111', 'X+1': '110111', 'D-1': '001110', 'X-1': '110010',
             'D+X': '000010', 'D-X': '010011', 'X-D': '000111', 'D&X': '000000', 'D|X': '010101'}

destTable = {'': '000', 'M': '001', 'D': '010', 'MD': '011', 'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'}

jmpTable = {'': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011', 'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}


# helper functions
def toBinary(num):
    s = bin(num).replace("0b", "")
    z = ""
    for i in range(15 - len(s)):
        z += "0"
    return z + s


# returns only the command part of the line, or empty
def parseLine(line):
    line = line.replace("\n", "")
    try:
        line = line[0:line.index("//")].strip()
    except ValueError:
        line = line.strip()

    return line


assemblyCode = open(f"{fileName}.asm", "r").readlines()
machineCode = []

lineNumber = -1
# first pass to get label names
for line in assemblyCode:
    l = parseLine(line)
    if len(l) > 0:
        lineNumber += 1
        if '(' in l and ')' in l:
            labelname = l[l.index('(') + 1: l.index(')')].strip()
            if labelname not in symbolTable:
                symbolTable[labelname] = lineNumber
            lineNumber -= 1

# second pass to construct machine code line by line
currentMemAddress = 16
for line in assemblyCode:
    line = parseLine(line)
    if len(line) > 0 and ('(' not in line):
        # A instruction
        if '@' in line:
            line = line[1:]
            try:
                address = str(toBinary(int(line)))
                machineCode.append(f'0{address}')
            except ValueError:
                if line in symbolTable:
                    address = toBinary(symbolTable[line])
                    machineCode.append(f'0{str(address)}')
                else:
                    symbolTable[line] = currentMemAddress
                    machineCode.append(f'0{toBinary(currentMemAddress)}')
                    currentMemAddress += 1
            machineCode.append('\n')
            continue
        # C instruction
        else:
            to_return = "111"

            eqIndex = 0
            colonIndex = 0
            try:
                eqIndex = line.index('=')
            except ValueError:
                eqIndex = -1
            try:
                colonIndex = line.index(';')
            except ValueError:
                colonIndex = -1
            if (colonIndex >= 0) and (eqIndex >= 0):
                comp = line[eqIndex + 1:colonIndex]
            elif (colonIndex >= 0) and (eqIndex == -1):
                comp = line[0:colonIndex]
            else:
                comp = line[eqIndex + 1:]
            if 'M' in comp:
                to_return += '1'
            else:
                to_return += '0'
            if comp[0] not in 'D' and ('+' in comp or '&' in comp or '|' in comp) and ('1' not in comp):
                comp = comp[::-1]
            comp = comp.replace('A', 'X').replace('M', 'X')
            to_return += compTable[comp]

            try:
                dest = line[0: line.index('=')]
                to_return += destTable[dest]
            except ValueError:
                to_return += '000'

            if colonIndex >= 0:
                jmp = line[colonIndex + 1:]
                jmp = jmpTable[jmp]
            else:
                jmp = "000"
            to_return += jmp
            machineCode.append(to_return)
            machineCode.append('\n')
    else:
        continue

# cool unecessary animation
total = int(len(machineCode) / 2) - 1
count = 0
for line in machineCode:
    if line != '\n':
        print(f"{count}/{total}:", end="")
        for c in line:
            print(c, end="")
            time.sleep(0.01)
        count += 1
        print('\n')

filePath = os.path.join(sys.path[0], f'Machine Languange Programs/{o_fileName}')
with open(f'{filePath}.hack', 'w') as f:
    f.writelines(machineCode)
    f.close()
input("Done")
