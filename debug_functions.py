import random
import pygame


def generateRandom16Bit():
    r = ''
    for i in range(16):
        r += str(random.randint(0, 1))
    return r


def generateADD16():
    print('Vars:')
    for i in range(16):
        print(f'{chr(99 + i)} = Bit(0)')
    s = 'FullAdder(a[0], b[0], Bit(0), out[0], c)\n'
    for i in range(16):
        s += f'FullAdder(Bit(a[{i + 1}]), Bit(b[{i + 1}]),{chr(99 + i)}, out.getBit({i + 1}), {chr(99 + i + 1)})\n'
    print(s)


def addressFromString(s):
    l = []
    for i in s[::-1]:
        l.append(Bit(int(i)))
    return l


def padded_binary(s: int):
    return bin(s)[2:].zfill(16)


def busToDecimal(s: str):
    s = s[s.index('(') + 1:s.index(')')]
    return s


def generateKeyFunc():
    for i in range(97, 97 + 27):
        s = f'''if keys[pygame.K_{chr(i)}]:
    return "{chr(i - 32)}"'''
        print(s)


def getCurrentKeyName(keys):
    if keys[pygame.K_a]:
        return "A"
    if keys[pygame.K_b]:
        return "B"
    if keys[pygame.K_c]:
        return "C"
    if keys[pygame.K_d]:
        return "D"
    if keys[pygame.K_e]:
        return "E"
    if keys[pygame.K_f]:
        return "F"
    if keys[pygame.K_g]:
        return "G"
    if keys[pygame.K_h]:
        return "H"
    if keys[pygame.K_i]:
        return "I"
    if keys[pygame.K_j]:
        return "J"
    if keys[pygame.K_k]:
        return "K"
    if keys[pygame.K_l]:
        return "L"
    if keys[pygame.K_m]:
        return "M"
    if keys[pygame.K_n]:
        return "N"
    if keys[pygame.K_o]:
        return "O"
    if keys[pygame.K_p]:
        return "P"
    if keys[pygame.K_q]:
        return "Q"
    if keys[pygame.K_r]:
        return "R"
    if keys[pygame.K_s]:
        return "S"
    if keys[pygame.K_t]:
        return "T"
    if keys[pygame.K_u]:
        return "U"
    if keys[pygame.K_v]:
        return "V"
    if keys[pygame.K_w]:
        return "W"
    if keys[pygame.K_x]:
        return "X"
    if keys[pygame.K_y]:
        return "Y"
    if keys[pygame.K_z]:
        return "Z"
    if keys[pygame.K_UP]:
        return 'up'
    if keys[pygame.K_LEFT]:
        return 'left'
    if keys[pygame.K_RIGHT]:
        return 'right'
    if keys[pygame.K_DOWN]:
        return 'down'
    if keys[pygame.K_SPACE]:
        return 'space'
    if keys[pygame.K_RETURN]:
        return 'newline'
    if keys[pygame.K_BACKSPACE]:
        return 'backspace'
    if keys[pygame.K_HOME]:
        return 'home'
    if keys[pygame.K_END]:
        return 'end'
    if keys[pygame.K_PAGEUP]:
        return 'pageup'
    if keys[pygame.K_PAGEDOWN]:
        return 'pagedown'
    if keys[pygame.K_INSERT]:
        return 'insert'
    if keys[pygame.K_DELETE]:
        return 'delete'
    if keys[pygame.K_ESCAPE]:
        return 'esc'
    return 'None'


def getKeyCode(k: str):
    num = 0
    if k == 'up':
        num = 131
    elif k == 'left':
        num = 130
    elif k == 'right':
        num = 132
    elif k == 'down':
        num = 133
    elif k == 'space':
        num = 32
    elif k == 'newline':
        num = 128
    elif k == 'backspace':
        num = 129
    elif k == 'home':
        num = 134
    elif k == 'end':
        num = 135
    elif k == 'pageup':
        num = 136
    elif k == 'pagedown':
        num = 137
    elif k == 'insert':
        num = 138
    elif k == 'delete':
        num = 139
    elif k == 'esc':
        num = 140
    elif k == 'None':
        return padded_binary(0)
    else:
        try:
            num = int(ord(k))
        except:
            return padded_binary(0)

    return padded_binary(num)


def binaryListAsInteger(s: list):
    s = ''.join([str(int(i)) for i in s[::-1][1:]])
    return int(s, 2)


def stringToTruthList(s: str):
    r = []
    for c in s[::-1]:
        r.append(True if c == '1' else False)
    r.append('1' in s)
    return r