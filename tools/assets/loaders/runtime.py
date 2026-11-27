"""What the generated loaders (analysis/<build>/assets/loaders_gen.py) run on: memory access, the C stack pointer,
string constants and indirect calls."""
import struct

from c_model import Mem


class Runtime:
    STACK = 0x7FFE00000000

    def __init__(self, mem: Mem, funcs, hooks):
        self.mem, self.funcs, self.hooks = mem, funcs, hooks
        self.sp = self.STACK
        self.strings = {}
        m = mem
        page_mask, pages, size = mem.PAGE - 1, mem.pages, mem.PAGE

        def ld(a, n, signed):
            o = a & page_mask
            if o + n <= size:
                pg = pages.get(a - o)
                if pg is None:
                    pg = m._page(a)
                return int.from_bytes(pg[o:o + n], 'little', signed=signed)
            return int.from_bytes(m.read(a, n), 'little', signed=signed)

        def st(a, n, v):
            b = (v & ((1 << (8 * n)) - 1)).to_bytes(n, 'little')
            o = a & page_mask
            if o + n <= size:
                pg = pages.get(a - o)
                if pg is None:
                    pg = m._page(a)
                pg[o:o + n] = b
            else:
                m.write(a, b)
        if type(mem) is Mem:
            self.ld, self.st = ld, st
        else:
            # a Mem subclass watching accesses (tests/assets/loaders_check.py): every access goes through it
            self.ld = lambda a, n, signed: int.from_bytes(m.read(a, n), 'little', signed=signed)
            self.st = lambda a, n, v: m.write(a, (v & ((1 << (8 * n)) - 1)).to_bytes(n, 'little'))

    def ldf(self, a, n):
        return struct.unpack('<f' if n == 4 else '<d', self.mem.read(a, n))[0]

    def stf(self, a, n, v):
        self.mem.write(a, struct.pack('<f' if n == 4 else '<d', v))

    def memset(self, d, v, n):
        self.mem.write(d, bytes([v & 0xFF]) * n)
        return d

    def memcpy(self, d, s, n):
        self.mem.write(d, self.mem.read(s, n))
        return d

    def cstring(self, s):
        a = self.strings.get(s)
        if a is None:
            a = self.strings[s] = 0x7FF100000000 + sum(len(k) for k in self.strings)
            self.mem.write(a, s)
        return a

    def call(self, target, args):
        h = self.hooks.get(target)
        if h is not None:
            return h(self, args)
        f = self.funcs.get(target)
        if f is None:
            self.untranslated(target)
        return f(*args)

    @staticmethod
    def untranslated(va):
        raise RuntimeError(f'{va:X} is outside the translated loaders (stand_ins.py TRANSLATED_*)')
