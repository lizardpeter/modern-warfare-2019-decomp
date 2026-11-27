"""Ghidra's decompiled C as data: its types, a paged byte memory, and one parsed function (docs/assets/loader-translation.md).

`Func` parses one function's pseudocode with pycparser after declaring Ghidra's type names, and records the
decompiler's own type for each global it uses (the `// global` lines Decompile.java writes).
"""
import re
import struct
from pycparser import c_ast, c_parser

PRE = '''typedef unsigned char undefined; typedef unsigned char undefined1; typedef unsigned short undefined2;
typedef unsigned int undefined4; typedef unsigned long long undefined8; typedef unsigned char byte;
typedef unsigned short ushort; typedef unsigned int uint; typedef unsigned long long ulonglong; typedef long long longlong;
typedef unsigned char bool; typedef unsigned long long size_t; typedef void code; typedef unsigned char uchar;
typedef unsigned int ulong; typedef unsigned short wchar16;
typedef int undefined3; typedef int undefined5; typedef int undefined6; typedef int undefined7;
typedef int uint3; typedef int uint5; typedef int uint6; typedef int uint7; typedef int int3; typedef int int5;
typedef int int6; typedef int int7; typedef int unkuint9; typedef int unkbyte9; typedef int unkuint10;
typedef unsigned int DWORD; typedef int BOOL; typedef void *HANDLE; typedef unsigned short WCHAR;
typedef long long __int64; typedef long long __time64_t; typedef int errno_t; typedef unsigned char BYTE;
typedef unsigned short WORD; typedef void *LPVOID; typedef char *LPCSTR; typedef char *LPSTR;
typedef unsigned long long ULONGLONG; typedef long long LONGLONG; typedef int LONG; typedef unsigned int UINT;
typedef void FILE; typedef unsigned short wchar_t;
'''
NPRE = PRE.count('\n')

# ---------------- types ----------------
I8, I16, I32, I64 = ('i', 1, True), ('i', 2, True), ('i', 4, True), ('i', 8, True)
U8, U16, U32, U64 = ('i', 1, False), ('i', 2, False), ('i', 4, False), ('i', 8, False)
VOID = ('v',)
BASE = {
    'char': I8, 'signed char': I8, 'unsigned char': U8, 'short': I16, 'unsigned short': U16, 'int': I32,
    'unsigned int': U32, 'long': I32, 'unsigned long': U32, 'long long': I64, 'unsigned long long': U64,
    'void': VOID, 'float': ('f', 4), 'double': ('f', 8), 'unsigned': U32, 'signed': I32,
    'undefined': U8, 'undefined1': U8, 'undefined2': U16, 'undefined4': U32, 'undefined8': U64, 'byte': U8,
    'ushort': U16, 'uint': U32, 'ulonglong': U64, 'longlong': I64, 'bool': U8, 'size_t': U64, 'code': VOID,
    'uchar': U8, 'ulong': U32, 'wchar16': U16,
    # Ghidra's odd-sized integers: their real width
    'undefined3': ('i', 3, False), 'undefined5': ('i', 5, False), 'undefined6': ('i', 6, False),
    'undefined7': ('i', 7, False), 'uint3': ('i', 3, False), 'uint5': ('i', 5, False), 'uint6': ('i', 6, False),
    'uint7': ('i', 7, False), 'int3': ('i', 3, True), 'int5': ('i', 5, True), 'int6': ('i', 6, True),
    'int7': ('i', 7, True), 'unkuint9': ('i', 9, False), 'unkbyte9': ('i', 9, False), 'unkuint10': ('i', 10, False),
    'DWORD': U32, 'BOOL': I32, 'HANDLE': ('p', VOID), 'WCHAR': U16, '__int64': I64, '__time64_t': I64,
    'errno_t': I32, 'BYTE': U8, 'WORD': U16, 'LPVOID': ('p', VOID), 'LPCSTR': ('p', I8), 'LPSTR': ('p', I8),
    'ULONGLONG': U64, 'LONGLONG': I64, 'LONG': I32, 'UINT': U32, 'FILE': VOID, 'wchar_t': U16,
}


def ptr(t):
    return ('p', t)


def sizeof(t):
    k = t[0]
    if k in ('i', 'f'):
        return t[1]
    if k == 'p' or k == 'fn':
        return 8
    if k == 'a':
        return sizeof(t[1]) * t[2]
    if k == 'v':
        return 1
    raise TypeError(t)


def ctype(node):
    """pycparser type node -> our type."""
    if isinstance(node, c_ast.Typename):
        return ctype(node.type)
    if isinstance(node, c_ast.TypeDecl):
        return ctype(node.type)
    if isinstance(node, c_ast.IdentifierType):
        return BASE[' '.join(node.names)]
    if isinstance(node, c_ast.PtrDecl):
        return ptr(ctype(node.type))
    if isinstance(node, c_ast.ArrayDecl):
        return ('a', ctype(node.type), int(node.dim.value, 0) if node.dim is not None else 0)
    if isinstance(node, c_ast.FuncDecl):
        return ('fn', ctype(node.type))
    raise TypeError(type(node))


def wrap(v, t):
    if t[0] == 'i':
        bits = 8 * t[1]
        v &= (1 << bits) - 1
        if t[2] and v >> (bits - 1):
            v -= 1 << bits
        return v
    if t[0] in ('p', 'fn'):
        return v & 0xFFFFFFFFFFFFFFFF
    if t[0] == 'f':
        return float(v)
    return v


def is_int(t):
    return t[0] == 'i'


def is_ptr(t):
    return t[0] in ('p', 'a', 'fn')


# ---------------- memory ----------------
class Mem:
    PAGE = 1 << 16

    def __init__(self, backing=None):
        self.pages = {}
        self.backing = backing        # callable(page_address) -> bytes or None (initial contents, e.g. the exe)

    def _page(self, a):
        p = a & ~(self.PAGE - 1)
        pg = self.pages.get(p)
        if pg is None:
            init = self.backing(p, self.PAGE) if self.backing else None
            pg = self.pages[p] = bytearray(init) if init else bytearray(self.PAGE)
        return pg

    def read(self, a, n):
        out = bytearray()
        while n:
            pg = self._page(a)
            o = a & (self.PAGE - 1)
            k = min(n, self.PAGE - o)
            out += pg[o:o + k]
            a += k
            n -= k
        return bytes(out)

    def write(self, a, b):
        i = 0
        while i < len(b):
            pg = self._page(a + i)
            o = (a + i) & (self.PAGE - 1)
            k = min(len(b) - i, self.PAGE - o)
            pg[o:o + k] = b[i:i + k]
            i += k

    def load(self, a, t):
        if t[0] == 'i':
            return int.from_bytes(self.read(a, t[1]), 'little', signed=t[2])
        if t[0] in ('p', 'fn'):
            return int.from_bytes(self.read(a, 8), 'little')
        if t[0] == 'f':
            return struct.unpack('<f' if t[1] == 4 else '<d', self.read(a, t[1]))[0]
        if t[0] == 'v':
            return int.from_bytes(self.read(a, 1), 'little')
        raise TypeError(t)

    def store(self, a, t, v):
        if t[0] == 'i':
            self.write(a, (v & ((1 << (8 * t[1])) - 1)).to_bytes(t[1], 'little'))
        elif t[0] in ('p', 'fn'):
            self.write(a, (v & 0xFFFFFFFFFFFFFFFF).to_bytes(8, 'little'))
        elif t[0] == 'f':
            self.write(a, struct.pack('<f' if t[1] == 4 else '<d', v))
        elif t[0] == 'v':
            self.write(a, bytes([v & 0xFF]))
        else:
            raise TypeError(t)


def labels_in(node, acc=None):
    if acc is None:
        acc = set()
    if isinstance(node, c_ast.Label):
        acc.add(node.name)
    for _, ch in node.children():
        labels_in(ch, acc)
    return acc


GLOBAL_RE = re.compile(r'^(?:_*DAT|PTR_DAT|PTR)_([0-9a-f]{8,9})$|^[a-z]+Ram([0-9a-f]{16})$')


class Func:
    def __init__(self, va, text):
        self.va = va
        # the decompiler's own type for each global (Decompile.java "globals", published as comment lines)
        self.decl_globals = {}
        for name, typ in re.findall(r'^// global (\S+) \S+ \S+ (.+?) \(\d+\)$', text, flags=re.M):
            if typ == '-':
                continue
            try:
                d = c_parser.CParser().parse(PRE + f'{typ} __g;').ext[-1]
                self.decl_globals[name] = ctype(d.type)
            except Exception:
                pass                     # a type pycparser cannot express (a struct): fall back as before
        body = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
        body = re.sub(r'^//.*$', '', body, flags=re.M)
        ast = c_parser.CParser().parse(PRE + body)
        self.fd = next(e for e in ast.ext if isinstance(e, c_ast.FuncDef))
        fdecl = self.fd.decl.type
        self.ret = ctype(fdecl.type)
        self.params = []
        if fdecl.args:
            for p in fdecl.args.params:
                if isinstance(p, c_ast.Typename):     # (void)
                    continue
                self.params.append((p.name, ctype(p.type)))
        self.locals = {}
        for item in self.fd.body.block_items or []:
            if isinstance(item, c_ast.Decl):
                self.locals[item.name] = ctype(item.type)
        self.labels = {}
        self.gtypes = dict(self.decl_globals)
        self._infer_globals()

    def _infer_globals(self):
        """A global of undefined type takes the type Ghidra gave it in this function: that of a local it is assigned
        to or from without a cast."""
        known = dict(self.params)
        known.update(self.locals)

        def visit(n):
            if isinstance(n, c_ast.Assignment) and n.op == '=':
                l, r = n.lvalue, n.rvalue
                if isinstance(l, c_ast.ID) and isinstance(r, c_ast.ID):
                    if l.name in known and GLOBAL_RE.match(r.name):
                        self.gtypes.setdefault(r.name, known[l.name])
                    elif r.name in known and GLOBAL_RE.match(l.name):
                        self.gtypes.setdefault(l.name, known[r.name])
                if isinstance(l, c_ast.ID) and GLOBAL_RE.match(l.name) and isinstance(r, c_ast.Cast):
                    self.gtypes.setdefault(l.name, ctype(r.to_type))
            for _, ch in n.children():
                visit(ch)
        visit(self.fd.body)


def gaddr(name):
    m = GLOBAL_RE.match(name)
    return int(m.group(1) or m.group(2), 16)


