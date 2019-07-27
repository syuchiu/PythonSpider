"""
@file:googleDecrypt.py
@time:2019/7/26-9:55
"""

import ctypes


# In [6]: ord("A")
# Out[6]: 65
#
# In [7]: chr(65)
# Out[7]: 'A'

def get_tk(tkk, text):
    d = tkk.split('.')
    b = int(d[0])

    e, f, g = {}, 0, 0

    for g in range(len(text)):

        h = ord(text[g])

        if 128 > h:
            e[f] = h
            f = f + 1

        else:
            if 2048 > h:
                e[f] = h >> 6 | 192
                f = f + 1
            else:
                if 55296 == (h & 64512) and g + 1 < len(text) and 56320 == (64512 & ord(text[g + 1]) & 64512):
                    g = g + 1
                    h = 65536 + ((h & 1023) << 10) + (ord(text[g]) & 1023)
                    e[f] = h >> 18 | 240
                    f = f + 1
                    e[f] = h >> 12 & 63 | 128
                    f = f + 1
                else:
                    e[f] = h >> 12 | 224
                    f = f + 1
                    e[f] = h >> 6 & 63 | 128
                    f = f + 1

                e[f] = h & 63 | 128
                f = f + 1

    a = b
    # "+-a^+6"
    for f in range(len(e)):
        a += e[f]
        a = uo(a, "+-a^+6")

    # "+-3^+b+-f"
    a = uo(a, "+-3^+b+-f")
    # print("---{}---".format(a))
    a ^= int(d[1]) or 0

    if 0 > a:
        a = (a & 2147483647) + 2147483648
    else:
        pass

    # print("---{}---".format(a))
    a = a % 1E6

    # print(str(int(a)) + "." + str((int(a) ^ b)))
    return str(int(a)) + "." + str(int(a) ^ b)


# 2133131264
def uo(a, b):
    for c in range(0, len(b) - 2, 3):
        d = b[c + 2]
        d = ord(d[0]) - 87 if "a" <= d else int(d)
        d = unsigned_right_shitf(a, d) if "+" == b[c + 1] else int_overflow(a << d)
        a = a + d & 4294967295 if "+" == b[c] else a ^ d
    return a


def int_overflow(val):
    maxint = 2147483647
    if not -maxint - 1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val


# 无符号右移
def unsigned_right_shitf(n, i):
    # 数字小于0，则转为32位无符号uint
    if n < 0:
        n = ctypes.c_uint32(n).value
    # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移好了
    if i < 0:
        return -int_overflow(n << abs(i))
    # print(n)
    return int_overflow(n >> i)


if __name__ == '__main__':
    tkk = "434497.1533999857"
    text = "你好"
    get_tk(tkk, text)
    # print(int_overflow(1345388106 << 15))
