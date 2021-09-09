import time

from debug_functions import generateRandom16Bit, busToDecimal, padded_binary, binaryListAsInteger, stringToTruthList


def addressFromString(s):
    l = []
    for i in s[::-1]:
        l.append(Bit(int(i)))
    return l


class Bit:
    def __init__(self, state: int = 0):
        self.state = state

    def set(self, newState: int):
        if type(newState) is bool:
            self.state = int(newState)
        else:
            self.state = newState

    def get(self):
        return bool(self.state)

    def __str__(self):
        return str(self.state)


class Bus:
    def __init__(self, startingStates=''):
        self.bits = []
        for i in range(16):
            a = Bit(0)
            self.bits.append(a)
        if len(startingStates) == 16:
            self.set(startingStates)
        self.oneExists = False

    def __getitem__(self, item):
        if type(item) is int:
            return bool(self.bits[item].get())
        elif type(item) is slice:
            return self.bits[item.start:item.stop]

    def __setitem__(self, key: int, value: int):
        if type(value) is bool:
            self.bits[key].set(int(value))
        else:
            self.bits[key].set(value)
        if value == 1:
            self.oneExists = True

    def __str__(self):
        r = ''
        for i in range(16):
            r += str(self.bits[16 - 1 - i])
        r += f' ({int(r, 2)})'
        return r

    # indexes from back to front. if input is 110, bus[0] is 0 and bus[2] is 1
    def set(self, bits):
        if len(bits) == 16:
            if type(bits) is str:
                for i in range(16):
                    self.bits[16 - 1 - i].set(int(bits[i]))
        else:
            z = '0' * (16 - len(bits))
            z += bits
            for i in range(16):
                self.bits[16 - 1 - i].set(int(z[i]))
        count = 0
        for b in self.bits:
            if b.get():
                self.oneExists = True
                break
            count += 1
        if count >= 16:
            self.oneExists = False

    def getBit(self, index):
        return self.bits[index]

    def setBit(self, index, newBit: Bit):
        self.bits[index] = Bit(int(str(newBit)))
        if newBit.get():
            self.oneExists = True


# all functions and classes used use 'pointers' instead of return statements to return values.
# this means that the variable storing the return value is passed along with the inputs
# elementary circuits---------------------------------------------------------------------------------------------------
def AND(a: Bit, b: Bit, out: Bit):
    out.set(a.get() and b.get())


def AND16(a: Bus, b: Bus, out: Bus):
    for i in range(16):
        out[i] = a[i] and b[i]


def OR(a: Bit, b: Bit, out: Bit):
    out.set(a.get() or b.get())


def OR16(a: Bus, b: Bus, out: Bus):
    for i in range(16):
        out[i] = a[i] or b[i]


def OR16Way(a: Bus, out: Bit):
    s = str(a)
    if '1' in s[0:s.index('(')]:
        out.set(1)
    else:
        out.set(0)


def MUX(a: Bit, b: Bit, sel: Bit, out: Bit):
    if sel.get():
        out.set(b.get())
    else:
        out.set(a.get())


def MUX16(a: Bus, b: Bus, sel: Bit, out: Bus):
    if sel.get():
        out.set(str(b))
    else:
        out.set(str(a))


def MUX4Way16(a: Bus, b: Bus, c: Bus, d: Bus, sel: list, out: Bus):
    q = Bus()
    r = Bus()
    MUX16(a, b, sel[0], q)
    MUX16(c, d, sel[0], r)
    MUX16(q, r, sel[1], out)


def MUX8Way16(a, b, c, d, e, f, g, h, sel, out):
    q = Bus()
    r = Bus()
    s = Bus()
    t = Bus()
    u = Bus()
    v = Bus()

    MUX16(a, b, sel[0], q)
    MUX16(c, d, sel[0], r)
    MUX16(e, f, sel[0], s)
    MUX16(g, h, sel[0], t)
    MUX16(q, r, sel[1], u)
    MUX16(s, t, sel[1], v)
    MUX16(u, v, sel[2], out)


def DMUX(inBit: Bit, sel: Bit, a: Bit, b: Bit):
    if sel.get():
        a.set(0)
        b.set(inBit.get())
    else:
        a.set(inBit.get())
        b.set(0)


def DMUX4Way(inBit: Bit, sel: list, a, b, c, d):
    ao = Bit(0)
    bo = Bit(0)
    DMUX(inBit, sel[1], ao, bo)
    DMUX(ao, sel[0], a, b)
    DMUX(bo, sel[0], c, d)


def DMUX8Way(inBit: Bit, sel: list, a, b, c, d, e, f, g, h):
    a0 = Bit(0)
    b0 = Bit(0)
    a1 = Bit(0)
    b1 = Bit(0)
    c1 = Bit(0)
    d1 = Bit(0)

    DMUX(inBit, sel[2], a0, b0)
    DMUX(a0, sel[1], a1, b1)
    DMUX(b0, sel[1], c1, d1)
    DMUX(a1, sel[0], a, b)
    DMUX(b1, sel[0], c, d)
    DMUX(c1, sel[0], e, f)
    DMUX(d1, sel[0], g, h)


def NOT(a: Bit, out: Bit):
    out.set(not a.get())


def NOT16(a: Bus, out: Bus):
    for i in range(16):
        out[i] = not a[i]


def XOR(a: Bit, b: Bit, out: Bit):
    out.set(a.get() != b.get())


# ----------------------------------------------------------------------------------------------------------------------

# arithmetic circuits-------------------------------------------------------------------------------------------------
def HalfAdder(a: Bit, b: Bit, s: Bit, c_out: Bit):
    XOR(a, b, s)
    AND(a, b, c_out)


def FullAdder(a: Bit, b: Bit, c_in: Bit, s: Bit, c_out: Bit):
    c1 = Bit(0)
    c2 = Bit(0)
    s1 = Bit(0)
    HalfAdder(a, b, s1, c1)
    HalfAdder(c_in, s1, s, c2)
    OR(c1, c2, c_out)


def ADD16(a: Bus, b: Bus, out: Bus):
    c = Bit(0)
    d = Bit(0)
    e = Bit(0)
    f = Bit(0)
    g = Bit(0)
    h = Bit(0)
    i = Bit(0)
    j = Bit(0)
    k = Bit(0)
    l = Bit(0)
    m = Bit(0)
    n = Bit(0)
    o = Bit(0)
    p = Bit(0)
    q = Bit(0)
    r = Bit(0)

    FullAdder(Bit(a[0]), Bit(b[0]), Bit(0), out.getBit(0), c)
    FullAdder(Bit(a[1]), Bit(b[1]), c, out.getBit(1), d)
    FullAdder(Bit(a[2]), Bit(b[2]), d, out.getBit(2), e)
    FullAdder(Bit(a[3]), Bit(b[3]), e, out.getBit(3), f)
    FullAdder(Bit(a[4]), Bit(b[4]), f, out.getBit(4), g)
    FullAdder(Bit(a[5]), Bit(b[5]), g, out.getBit(5), h)
    FullAdder(Bit(a[6]), Bit(b[6]), h, out.getBit(6), i)
    FullAdder(Bit(a[7]), Bit(b[7]), i, out.getBit(7), j)
    FullAdder(Bit(a[8]), Bit(b[8]), j, out.getBit(8), k)
    FullAdder(Bit(a[9]), Bit(b[9]), k, out.getBit(9), l)
    FullAdder(Bit(a[10]), Bit(b[10]), l, out.getBit(10), m)
    FullAdder(Bit(a[11]), Bit(b[11]), m, out.getBit(11), n)
    FullAdder(Bit(a[12]), Bit(b[12]), n, out.getBit(12), o)
    FullAdder(Bit(a[13]), Bit(b[13]), o, out.getBit(13), p)
    FullAdder(Bit(a[14]), Bit(b[14]), p, out.getBit(14), q)
    FullAdder(Bit(a[15]), Bit(b[15]), q, out.getBit(15), r)


def INC16(a, out):
    b = Bus()
    b.set('1')
    ADD16(a, b, out)


def ALU(x: Bus, y: Bus, zx: Bit, nx: Bit, zy: Bit, ny: Bit, f: Bit, no: Bit, out: Bus, zr: Bit, ng: Bit):
    zerox = Bus()
    zeros = Bus()
    # zero x input?
    MUX16(x, zeros, zx, zerox)

    # negate the x input?
    notx = Bus()
    finalx = Bus()
    NOT16(zerox, notx)
    MUX16(zerox, notx, nx, finalx)

    # zero the y input?
    zeroy = Bus()
    MUX16(y, zeros, zy, zeroy)

    # negate the y input?
    noty = Bus()
    finaly = Bus()
    NOT16(zeroy, noty)
    MUX16(zeroy, noty, ny, finaly)

    # x+y or x&y
    anded = Bus()
    added = Bus()
    finalout = Bus()
    ADD16(finalx, finaly, added)
    AND16(finalx, finaly, anded)
    MUX16(anded, added, f, finalout)

    # negate the output?
    notout = Bus()
    fout = Bus()
    NOT16(finalout, notout)
    MUX16(finalout, notout, no, fout)

    # is the output zeros? uses or16way usually
    if '1' not in str(fout):
        zr.set(1)
    else:
        zr.set(0)

    # is the output negative? uses sub-busing usually, and an or gate
    if str(fout.getBit(15)) == '1':
        ng.set(1)
    else:
        ng.set(0)

    # uses an or with false usually, because of how wires work
    out.set(str(fout))


# ----------------------------------------------------------------------------------------------------------------------

# sequential circuits---------------------------------------------------------------------------------------------------
# must use classes here as persistent 'storage' of data cant be implemented with methods, and each circuits output depends on
# previous inputs

# because of the chosen implementation, there is no distinction between fetch and execute cycles - everything happens instantly.
# instead, the order of inputs and outputs can be adjusted.
class BitRegister:
    def __init__(self):
        self.storedBit = Bit(0)

    def input(self, inBit: Bit, load: Bit):
        if load.get():
            self.storedBit.set(inBit.get())

    def output(self, out: Bit):
        out.set(self.storedBit.get())


class Register:
    def __init__(self):
        self.b_regs = []
        for i in range(16):
            self.b_regs.append(BitRegister())

    def input(self, inBus: Bus, load: Bit):
        for i in range(16):
            self.b_regs[i].input(inBus.getBit(i), load)

    def output(self, output: Bus):
        for i in range(16):
            currentBit = output.getBit(i)
            self.b_regs[i].output(currentBit)
            output.setBit(i, currentBit)


# unused. helps simulating a clocked circuit.
class RegisterClocked:
    def __init__(self):
        # old and new values
        self.o_regs = Bus()
        self.n_regs = Bus()

    def input(self, inBus: Bus, load: Bit):
        if load.get():
            s = str(inBus)
            self.n_regs = Bus(s[:s.index('(') - 1])

    def output(self, output: Bus):
        for i in range(16):
            output.setBit(i, self.o_regs.getBit(i))

        for i in range(16):
            self.o_regs.setBit(i, self.n_regs.getBit(i))


# uses cascading address bits; so a call to RAM16K will eventually call RAM8, Register, and BitRegister
class RAM8:
    def __init__(self):
        self.regs = []
        for i in range(8):
            self.regs.append(Register())

    def input(self, inBus: Bus, load: Bit, address: list):
        a = Bit()
        b = Bit()
        c = Bit()
        d = Bit()
        e = Bit()
        f = Bit()
        g = Bit()
        h = Bit()

        DMUX8Way(load, address, a, b, c, d, e, f, g, h)

        self.regs[0].input(inBus, a)
        self.regs[1].input(inBus, b)
        self.regs[2].input(inBus, c)
        self.regs[3].input(inBus, d)
        self.regs[4].input(inBus, e)
        self.regs[5].input(inBus, f)
        self.regs[6].input(inBus, g)
        self.regs[7].input(inBus, h)

    def output(self, output: Bus, address: list):
        a = Bus()
        b = Bus()
        c = Bus()
        d = Bus()
        e = Bus()
        f = Bus()
        g = Bus()
        h = Bus()

        self.regs[0].output(a)
        self.regs[1].output(b)
        self.regs[2].output(c)
        self.regs[3].output(d)
        self.regs[4].output(e)
        self.regs[5].output(f)
        self.regs[6].output(g)
        self.regs[7].output(h)

        MUX8Way16(a, b, c, d, e, f, g, h, address, output)


class RAM64:
    def __init__(self):
        self.ram = []
        for i in range(8):
            self.ram.append(RAM8())

    # address is 6 bits
    def input(self, inBus: Bus, load: Bit, address: list):
        a = Bit()
        b = Bit()
        c = Bit()
        d = Bit()
        e = Bit()
        f = Bit()
        g = Bit()
        h = Bit()

        DMUX8Way(load, address[3:6], a, b, c, d, e, f, g, h)

        self.ram[0].input(inBus, a, address[0:3])
        self.ram[1].input(inBus, b, address[0:3])
        self.ram[2].input(inBus, c, address[0:3])
        self.ram[3].input(inBus, d, address[0:3])
        self.ram[4].input(inBus, e, address[0:3])
        self.ram[5].input(inBus, f, address[0:3])
        self.ram[6].input(inBus, g, address[0:3])
        self.ram[7].input(inBus, h, address[0:3])

    def output(self, output: Bus, address: list):
        a = Bus()
        b = Bus()
        c = Bus()
        d = Bus()
        e = Bus()
        f = Bus()
        g = Bus()
        h = Bus()

        self.ram[0].output(a, address[0:3])
        self.ram[1].output(b, address[0:3])
        self.ram[2].output(c, address[0:3])
        self.ram[3].output(d, address[0:3])
        self.ram[4].output(e, address[0:3])
        self.ram[5].output(f, address[0:3])
        self.ram[6].output(g, address[0:3])
        self.ram[7].output(h, address[0:3])

        MUX8Way16(a, b, c, d, e, f, g, h, address[3:6], output)


class RAM512:
    def __init__(self):
        self.ram = []
        for i in range(8):
            self.ram.append(RAM64())

    # address has 9 bits
    def input(self, inBus: Bus, load: Bit, address: list):
        a = Bit()
        b = Bit()
        c = Bit()
        d = Bit()
        e = Bit()
        f = Bit()
        g = Bit()
        h = Bit()

        DMUX8Way(load, address[6:9], a, b, c, d, e, f, g, h)

        self.ram[0].input(inBus, a, address[0:6])
        self.ram[1].input(inBus, b, address[0:6])
        self.ram[2].input(inBus, c, address[0:6])
        self.ram[3].input(inBus, d, address[0:6])
        self.ram[4].input(inBus, e, address[0:6])
        self.ram[5].input(inBus, f, address[0:6])
        self.ram[6].input(inBus, g, address[0:6])
        self.ram[7].input(inBus, h, address[0:6])

    def output(self, output: Bus, address: list):
        a = Bus()
        b = Bus()
        c = Bus()
        d = Bus()
        e = Bus()
        f = Bus()
        g = Bus()
        h = Bus()

        self.ram[0].output(a, address[0:6])
        self.ram[1].output(b, address[0:6])
        self.ram[2].output(c, address[0:6])
        self.ram[3].output(d, address[0:6])
        self.ram[4].output(e, address[0:6])
        self.ram[5].output(f, address[0:6])
        self.ram[6].output(g, address[0:6])
        self.ram[7].output(h, address[0:6])

        MUX8Way16(a, b, c, d, e, f, g, h, address[6:9], output)


class RAM4K:
    def __init__(self):
        self.ram = []
        for i in range(8):
            self.ram.append(RAM512())

    # address has 12 bits
    def input(self, inBus: Bus, load: Bit, address: list):
        a = Bit()
        b = Bit()
        c = Bit()
        d = Bit()
        e = Bit()
        f = Bit()
        g = Bit()
        h = Bit()

        DMUX8Way(load, address[9:12], a, b, c, d, e, f, g, h)

        self.ram[0].input(inBus, a, address[0:9])
        self.ram[1].input(inBus, b, address[0:9])
        self.ram[2].input(inBus, c, address[0:9])
        self.ram[3].input(inBus, d, address[0:9])
        self.ram[4].input(inBus, e, address[0:9])
        self.ram[5].input(inBus, f, address[0:9])
        self.ram[6].input(inBus, g, address[0:9])
        self.ram[7].input(inBus, h, address[0:9])

    def output(self, output: Bus, address: list):
        a = Bus()
        b = Bus()
        c = Bus()
        d = Bus()
        e = Bus()
        f = Bus()
        g = Bus()
        h = Bus()

        self.ram[0].output(a, address[0:9])
        self.ram[1].output(b, address[0:9])
        self.ram[2].output(c, address[0:9])
        self.ram[3].output(d, address[0:9])
        self.ram[4].output(e, address[0:9])
        self.ram[5].output(f, address[0:9])
        self.ram[6].output(g, address[0:9])
        self.ram[7].output(h, address[0:9])

        MUX8Way16(a, b, c, d, e, f, g, h, address[9:12], output)


class RAM16K:
    def __init__(self):
        self.ram = []
        for i in range(4):
            self.ram.append(RAM4K())

    # address has 14 bits
    def input(self, inBus: Bus, load: Bit, address: list):
        a = Bit()
        b = Bit()
        c = Bit()
        d = Bit()

        DMUX4Way(load, address[12:14], a, b, c, d)

        self.ram[0].input(inBus, a, address[0:12])
        self.ram[1].input(inBus, b, address[0:12])
        self.ram[2].input(inBus, c, address[0:12])
        self.ram[3].input(inBus, d, address[0:12])

    def output(self, output: Bus, address: list):
        a = Bus()
        b = Bus()
        c = Bus()
        d = Bus()

        self.ram[0].output(a, address[0:12])
        self.ram[1].output(b, address[0:12])
        self.ram[2].output(c, address[0:12])
        self.ram[3].output(d, address[0:12])

        MUX4Way16(a, b, c, d, address[12:14], output)


class PC:
    def __init__(self):
        self.state = Bus()

    def input(self, inBus: Bus, load: Bit, inc: Bit, reset: Bit):
        incd = Bus()
        INC16(self.state, incd)
        incornot = Bus()
        MUX16(self.state, incd, inc, incornot)

        loadornot = Bus()
        MUX16(incornot, inBus, load, loadornot)

        zeros = Bus('0000000000000000')
        MUX16(loadornot, zeros, reset, self.state)

    def output(self, output: Bus):
        for i in range(16):
            output.setBit(i, self.state.getBit(i))


# custom implementation for performance
class ROM32K:
    def __init__(self):
        self.ram = []
        for i in range(32768):
            self.ram.append(Bus())

    def getItemAtLocation(self, address: Bus, output: Bus):
        s = str(address)[1: str(address).index('(') - 1]

        busToReturn = self.ram[int(s, 2)]

        for i in range(16):
            output.setBit(i, busToReturn.getBit(i))


# emits ascii keycode of currently pressed key
class Keyboard:
    def __init__(self):
        self.state = Bus()

    def getState(self, output: Bus):
        for i in range(16):
            output.setBit(i, self.state.getBit(i))

    def setState(self, newState: str):
        self.state.set(newState)


# custom implementation for performance. usually uses a 8 kb RAM chip for a 512x256 screen
# however using a RAM class would make reading from memory terribly slow.
class Screen:
    def __init__(self):
        self.memory = []
        for i in range(8192):
            self.memory.append(Bus())

    # 13 bit address
    def input(self, inBus: Bus, load: Bit, address: list):
        s = ''
        for b in address[::-1]:
            s += str(b)
        if load.get():
            for i in range(16):
                self.memory[int(s, 2)].setBit(i, inBus.getBit(i))

    def output(self, output: Bus, address: list):
        s = ''
        for b in address:
            s += str(b)
        for i in range(16):
            output.setBit(i, self.memory[int(s, 2)].getBit(i))


# to avoid cascading, uses direct access. This is the class thats finally used. It can be swapped for the regular implementation
# if speed is not important, however one would have to rewrite a significant portion of the code
class RAM16KAlt:
    def __init__(self):
        self.ram = []
        for i in range(16384):
            self.ram.append(Bus())
        e = time.time()

    def input(self, inBus: Bus, load: Bit, address: list):
        s = ''
        for b in address[::-1]:
            s += str(b)
        if load.get():
            for i in range(16):
                self.ram[int(s, 2)].setBit(i, inBus.getBit(i))

    def output(self, output: Bus, address: list):
        s = ''
        for b in address[::-1]:
            s += str(b)
        index = int(s, 2)
        for i in range(16):
            output.setBit(i, self.ram[index].getBit(i))


# ----------------------------------------------------------------------------------------------------------------------

# assembling the parts for the computer---------------------------------------------------------------------------------
class Memory:
    def __init__(self):
        self.mem = RAM16KAlt()
        self.screen = Screen()
        self.keyboard = Keyboard()

    # 15 bit address
    def input(self, inBus: Bus, load: Bit, address: Bus):
        a = Bit()
        b = Bit()
        c = Bit()
        d = Bit()

        address = address.bits[:]

        DMUX4Way(load, address[13:15], a, b, c, d)
        OR(a, b, a)

        self.mem.input(inBus, a, address[0:14])
        self.screen.input(inBus, c, address[0:13])

    def output(self, output: Bus, address: Bus):
        a = Bus()
        c = Bus()
        d = Bus()

        address = address.bits[:]

        self.mem.output(a, address[0:14])
        self.screen.output(c, address[0:13])
        self.keyboard.getState(d)

        MUX4Way16(a, a, c, d, address[13:15], output)


# set debugPins to True to enable printing of a few inputs/outputs of internal chips
def CPU(inM: Bus, instruction: Bus, reset: Bit, outM: Bus, writeM: Bit, addressM: Bus, pcAddress: Bus,
        ARegister: Register,
        DRegister: Register, programCounter: PC, debugPins=False):
    b_instruction = instruction.bits

    if debugPins:
        print(f'Address: {busToDecimal(str(pcAddress))}, Instruction: {instruction}')

    # handling y input of ALU. Takes from AReg if instruction[12] is 0, else inM
    ALUYInput = Bus()
    MUX16(addressM, inM, b_instruction[12], ALUYInput)

    ALUzr = Bit()
    ALUng = Bit()
    DRegOut = Bus()
    DRegister.output(DRegOut)
    ALU(DRegOut, ALUYInput, b_instruction[11], b_instruction[10], b_instruction[9], b_instruction[8], b_instruction[7],
        b_instruction[6], outM, ALUzr, ALUng)

    if debugPins:
        print(f'ALU output: {outM}')

    # loading into A register
    MuxToAReg = Bus()
    notIcode = Bit()
    ARegLoad = Bit()

    MUX16(instruction, outM, b_instruction[15], MuxToAReg)
    NOT(b_instruction[15], notIcode)
    OR(notIcode, b_instruction[5], ARegLoad)
    if debugPins:
        print('A reg: \n')
        print(f'Input: MuxToAReg: {MuxToAReg}, ToLoad: {ARegLoad}')
    ARegister.input(MuxToAReg, ARegLoad)
    ARegister.output(addressM)
    if debugPins:
        print(f'A register output: {addressM}')

    # writeM is true if instruction[3] is true
    AND(b_instruction[15], b_instruction[3], writeM)

    # loading into D register
    # will only load if instruction[4] is true, and the msb is 1
    toLoadD = Bit()
    AND(b_instruction[15], b_instruction[4], toLoadD)

    # usually you cant connect output pins like addressM to internal circuits, but we'll do it for sake of simplicity.
    # instead, the ALU would have two outputs- one going to outM, and the other going to the D register.
    if debugPins:
        print(f'DRegister:\n')
        print(f'Input: Address: {outM}, toLoad: {toLoadD}')
    DRegister.input(outM, toLoadD)
    if debugPins:
        print(f'D register output: {DRegOut}')

    # handling program counter
    # the expression is C(D'E + BE') + A(D'E + BE) + A'BDE', to figure out whether to jump or not
    # A = instruction[2], B= instruction[1], C= instruction[0], D= ALUzr, E= ALUng
    # alternatively, you can use the function F(E'D'C + BD + AE) (f = instruction[15]). this is what ill use
    # you can do this with gates, but ill use pythons boolean functions
    A = b_instruction[2].get()
    B = b_instruction[1].get()
    C = b_instruction[0].get()
    D = ALUzr.get()
    E = ALUng.get()
    F = b_instruction[15].get()

    firstTerm = (not E) and (not D) and C
    secondTerm = B and D
    thirdTerm = A and E

    toJump = (firstTerm or secondTerm or thirdTerm) and F
    toJump = Bit(int(toJump))
    # if leftmost bit is 0, you dont jump
    # setting up inputs to PC
    PCIn = Bus()
    PCLoad = Bit()
    PCInc = Bit()
    MUX16(addressM, Bus('000000000000000'), reset, PCIn)

    OR(reset, toJump, PCLoad)

    NOT(PCLoad, PCInc)
    programCounter.input(PCIn, PCLoad, PCInc, reset)
    programCounter.output(pcAddress)
    if debugPins:
        print('------------------------------------------------------------------------------------------\n')


# different implementations of the CPU and ALU. These use entirely different data structures and flows, and favor
# speed (by not calling functions) to real life accuracy.
# i only spent a couple hours on this data flow, so using these is not recommended unless working with the screen.
def ALUFast(x, y, zx, nx, zy, ny, f, no):
    if zx:
        x = [0] * 17

    if nx:
        for i in range(17):
            x[i] = not x[i]

    if zy:
        y = [0] * 17

    if ny:
        for i in range(17):
            y[i] = not y[i]

    out = []
    if f:
        # reversing inputs and converting to numbers
        s1 = ''.join([str(int(i)) for i in x[::-1][1:]])
        s2 = ''.join([str(int(i)) for i in y[::-1][1:]])

        s1 = int(s1, 2)
        s2 = int(s2, 2)

        b = padded_binary(s1 + s2)[::-1]

        for bit in b:
            if bit == '1':
                out.append(True)
            else:
                out.append(False)
        out.append(s1 + s2 > 0)
    else:
        for i in range(16):
            out.append(x[i] and y[i])
        out.append(x[16] or y[16])

    if no:
        for i in range(17):
            out[i] = not out[i]

    zr = not out[16]
    ng = out[15]

    return [out, zr, ng]


def CPUFast(inM, instruction, reset, outM, writeM, addressM, pcAddress, ARegister, DRegister, debug=False):
    ALUYInput = []
    if debug:
        print(f'Address: {pcAddress}, Instruction: {instruction[::-1]}')
    instruction = [True if i == '1' else False for i in instruction]
    if instruction[12]:
        ALUYInput = inM[:]
    else:
        ALUYInput = addressM
    if debug:
        print(f'ALU Y Input: {["1" if i else "0" for i in ALUYInput[::-1][1:]]}')
    ALUo = ALUFast(DRegister, ALUYInput, instruction[11], instruction[10], instruction[9], instruction[8],
                   instruction[7],
                   instruction[6])

    for i in range(17):
        outM[i] = ALUo[0][i]
    if debug:
        print(f'ALU Output: {["1" if i else "0" for i in outM[::-1][1:]]}')
    ALUzr = ALUo[1]
    ALUng = ALUo[2]

    # loading into A register

    if (not instruction[15]) or instruction[5]:
        ARegIn = [False] * 17
        if instruction[15]:
            for i in range(17):
                ARegIn[i] = outM[i]
        else:
            for i in range(16):
                ARegIn[i] = instruction[i]
            ARegIn[16] = True
        for i in range(17):
            ARegister[i] = ARegIn[i]

    for i in range(17):
        addressM[i] = ARegister[i]
    if debug:
        print(f'AReg Output: {["1" if i else "0" for i in addressM[::-1][1:]]}')
    writeM[0] = instruction[3] and instruction[15]

    # loading into D register
    if instruction[15] and instruction[4]:
        for i in range(17):
            DRegister[i] = outM[i]
    if debug:
        print(f'DReg Output: {["1" if i else "0" for i in DRegister[::-1][1:]]}')
    # handling program counter
    A = instruction[2]
    B = instruction[1]
    C = instruction[0]
    D = ALUzr
    E = ALUng
    F = instruction[15]

    firstTerm = (not E) and (not D) and C
    secondTerm = B and D
    thirdTerm = A and E

    toJump = (firstTerm or secondTerm or thirdTerm) and F

    PCin = []
    if reset[0]:
        PCin = 0
    else:
        PCin = binaryListAsInteger(addressM)

    PCLoad = reset[0] or toJump
    if PCLoad:
        pcAddress[0] = PCin
    else:
        pcAddress[0] += 1
    if debug:
        print(f'PCADDRES: {pcAddress[0]}, WriteM: {writeM[0]}')

        print('-----------------------------------------------------------')