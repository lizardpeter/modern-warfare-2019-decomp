"""Compile Ghidra's decompiled C into Python closures, with every C type resolved once (docs/assets/loader-translation.md).

`Machine` holds the memory, the hooks (Python stand-ins by address) and the compiled functions; a function is parsed
and compiled the first time it is called.
"""
import struct
from pycparser import c_ast
from c_model import (Func, ctype, sizeof, wrap, ptr, GLOBAL_RE, gaddr, I8, I32, I64, U8, U64, VOID, labels_in)


class Goto(Exception):
    def __init__(self, label):
        self.label = label


class Ret(Exception):
    __slots__ = ('v',)

    def __init__(self, v):
        self.v = v


class Brk(Exception):
    pass


class Cont(Exception):
    pass


def promote(t):
    return I32 if t[0] == 'i' and t[1] < 4 else t


def common(a, b):
    if a[0] == 'f' or b[0] == 'f':
        return ('f', max(a[1] if a[0] == 'f' else 0, b[1] if b[0] == 'f' else 0))
    a, b = promote(a), promote(b)
    if a[1] != b[1]:
        return a if a[1] > b[1] else b
    if not a[2] or not b[2]:
        return ('i', a[1], False)
    return a


def decay(t):
    return ptr(t[1]) if t[0] == 'a' else t


def isptr(t):
    return t[0] in ('p', 'a', 'fn')


def wrapper_for(t):
    if t[0] == 'i':
        bits = 8 * t[1]
        m = (1 << bits) - 1
        if t[2]:
            h, full = 1 << (bits - 1), 1 << bits
            return lambda v: ((v & m) - full) if (v & m) & h else (v & m)
        return lambda v: v & m
    if t[0] in ('p', 'fn'):
        return lambda v: v & 0xFFFFFFFFFFFFFFFF
    if t[0] == 'f':
        return float
    return lambda v: v


def ghidra_op(name, afs, args):
    """Ghidra's pseudo-operators (Ghidra docs, "Decompiler: pseudo-operators"): CONCATxy(a, b) joins an x-byte a
    above a y-byte b; SUBxy(v, k) is y bytes of the x-byte v starting at byte k; ZEXTxy / SEXTxy widen x bytes to y."""
    import re
    if name == 'POPCOUNT':          # number of set bits
        v = afs[0]
        return I32, lambda env: bin(v(env) & 0xFFFFFFFFFFFFFFFF).count('1')
    m = re.fullmatch(r'(CONCAT|SUB|ZEXT|SEXT)(\d)(\d+)', name)
    if not m:
        return None
    kind, x, y = m.group(1), int(m.group(2)), int(m.group(3))
    if kind == 'CONCAT':
        a, b = afs
        mx, my = (1 << (8 * x)) - 1, (1 << (8 * y)) - 1
        t = ('i', x + y, False)
        return t, lambda env: ((a(env) & mx) << (8 * y)) | (b(env) & my)
    if kind == 'SUB':
        v, k = afs
        my = (1 << (8 * y)) - 1
        return ('i', y, False), lambda env: (v(env) >> (8 * k(env))) & my
    v = afs[0]
    mx = (1 << (8 * x)) - 1
    if kind == 'ZEXT':
        return ('i', y, False), lambda env: v(env) & mx
    h = 1 << (8 * x - 1)
    w = wrapper_for(('i', y, True))
    return ('i', y, True), lambda env: w(((v(env) & mx) ^ h) - h)


class Machine:
    """Memory + call dispatch shared by every compiled function."""
    STACK = 0x7FFE00000000

    def __init__(self, mem, source, hooks, recorded_types=None):
        self.mem, self.source, self.hooks = mem, source, hooks
        self.compiled = {}
        self.parsed_cache = {}
        self.parse_errors = {}
        self.gsym = recorded_types or {}      # address -> type Ghidra recorded for it (symbols.tsv), the fallback
        self.sp = self.STACK
        self.strings = {}
        self.calls = 0
        m = mem

        def mk_load(t):
            if t[0] == 'i':
                n, s = t[1], t[2]
                return lambda a: int.from_bytes(m.read(a, n), 'little', signed=s)
            if t[0] in ('p', 'fn'):
                return lambda a: int.from_bytes(m.read(a, 8), 'little')
            if t[0] == 'f':
                f = '<f' if t[1] == 4 else '<d'
                n = t[1]
                return lambda a: struct.unpack(f, m.read(a, n))[0]
            if t[0] == 'v':
                return lambda a: m.read(a, 1)[0]
            raise TypeError(t)

        def mk_store(t):
            if t[0] == 'i' or t[0] == 'v':
                n = t[1] if t[0] == 'i' else 1
                mask = (1 << (8 * n)) - 1
                return lambda a, v: m.write(a, (v & mask).to_bytes(n, 'little'))
            if t[0] in ('p', 'fn'):
                return lambda a, v: m.write(a, (v & 0xFFFFFFFFFFFFFFFF).to_bytes(8, 'little'))
            if t[0] == 'f':
                f = '<f' if t[1] == 4 else '<d'
                return lambda a, v: m.write(a, struct.pack(f, v))
            raise TypeError(t)
        self.mk_load, self.mk_store = mk_load, mk_store

    def parsed(self, va):
        f = self.parsed_cache.get(va, 0)
        if f == 0:
            text = self.source(va)
            try:
                f = Func(va, text) if text is not None else None
            except Exception as e:      # not C pycparser accepts; fatal only if the function is actually run
                self.parse_errors[va] = e
                f = None
            self.parsed_cache[va] = f
        return f

    def func(self, va):
        c = self.compiled.get(va)
        if c is None:
            f = self.parsed(va)
            if f is None:
                raise RuntimeError(f'{va:X}: ' + (f'pseudocode does not parse: {self.parse_errors[va]}'
                                                  if va in self.parse_errors else 'no pseudocode'))
            c = self.compiled[va] = Compiled(self, f)
        return c

    def call(self, va, args):
        self.calls += 1
        h = self.hooks.get(va)
        if h is not None:
            return h(self, args)
        return self.func(va).run(args)

    def cstring(self, s):
        a = self.strings.get(s)
        if a is None:
            a = self.strings[s] = 0x7FF100000000 + sum(len(k) for k in self.strings)
            self.mem.write(a, s)
        return a


class Compiled:
    def __init__(self, M, f: Func):
        self.M, self.f = M, f
        self.ret = f.ret
        self.params = f.params
        addr_taken = set()

        def scan(n):
            if isinstance(n, c_ast.UnaryOp) and n.op == '&' and isinstance(n.expr, c_ast.ID):
                addr_taken.add(n.expr.name)
            for _, ch in n.children():
                scan(ch)
        scan(f.fd.body)
        # every local and parameter: a Python slot, or (address taken / array) a frame offset
        self.slots, self.mems, off = {}, {}, 0
        for name, t in f.params + list(f.locals.items()):
            if name in addr_taken or t[0] == 'a':
                off += (sizeof(t) + 15) & ~15
                self.mems[name] = (off, t)
            else:
                self.slots[name] = (len(self.slots), t)
        self.frame_size = off + 0x40
        self.nslots = len(self.slots)
        self.pwrap = [wrapper_for(t) for _, t in f.params]
        self.rwrap = wrapper_for(self.ret) if self.ret[0] in ('i', 'p') else (lambda v: v)
        self.body = self.block(f.fd.body)

    # --- running ---
    def run(self, args):
        M = self.M
        base = M.sp
        M.sp = base - self.frame_size
        env = [0] * self.nslots
        env.append(base)              # env[-1]: frame base for memory locals
        try:
            for i, (name, t) in enumerate(self.params):
                v = args[i] if i < len(args) else 0
                v = self.pwrap[i](v)
                if name in self.slots:
                    env[self.slots[name][0]] = v
                else:
                    o, tt = self.mems[name]
                    M.mk_store(tt)(base - o, v)
            try:
                self.body(env)
                r = 0
            except Ret as e:
                r = e.v
            return self.rwrap(r) if not isinstance(r, float) else r
        finally:
            M.sp = base

    # --- statements: each compiles to fn(env) ---
    def block(self, node):
        items = node.block_items or []
        fns = [self.stmt(it) for it in items]
        labs = [labels_in(it) for it in items]
        entries = [self.entry(it) for it in items]
        alllabs = set().union(*labs) if labs else set()

        def run_from(env, i, label):
            while i < len(fns):
                try:
                    if label is not None:
                        lab, label = label, None
                        entries[i](env, lab)
                    else:
                        fns[i](env)
                except Goto as g:
                    if g.label not in alllabs:
                        raise
                    i = next(j for j, L in enumerate(labs) if g.label in L)
                    label = g.label
                    continue
                i += 1

        def run(env):
            run_from(env, 0, None)

        def enter(env, label):
            i = next(j for j, L in enumerate(labs) if label in L)
            run_from(env, i, label)
        run.enter = enter
        return run

    def entry(self, n):
        """fn(env, label): run n starting at label inside it."""
        if isinstance(n, c_ast.Label):
            inner = self.stmt(n.stmt)
            sub = self.entry(n.stmt)
            name = n.name
            return lambda env, l: inner(env) if l == name else sub(env, l)
        if isinstance(n, c_ast.Compound):
            b = self.block(n)
            return b.enter
        if isinstance(n, c_ast.If):
            t = self.entry(n.iftrue) if n.iftrue is not None else None
            fl = self.entry(n.iffalse) if n.iffalse is not None else None
            tl = labels_in(n.iftrue) if n.iftrue is not None else set()
            return lambda env, l: t(env, l) if l in tl else fl(env, l)
        if isinstance(n, (c_ast.While, c_ast.DoWhile, c_ast.For)):
            body = self.entry(n.stmt)
            loop = self.loop(n, skip_first_cond=False)
            nxt = self.expr(n.next)[1] if isinstance(n, c_ast.For) and n.next is not None else None

            def go(env, l):
                try:
                    body(env, l)
                except Brk:
                    return
                except Cont:
                    pass
                if nxt:
                    nxt(env)
                loop(env)
            return go
        return lambda env, l: (_ for _ in ()).throw(NotImplementedError(f'goto into {type(n).__name__}'))

    def loop(self, n, skip_first_cond=False):
        body = self.stmt(n.stmt)
        cond = self.cond(n.cond) if n.cond is not None else (lambda env: True)
        nxt = self.expr(n.next)[1] if isinstance(n, c_ast.For) and n.next is not None else None
        dowhile = isinstance(n, c_ast.DoWhile)

        def run(env):
            while True:
                if not dowhile and not cond(env):
                    return
                try:
                    body(env)
                except Brk:
                    return
                except Cont:
                    pass
                if nxt:
                    nxt(env)
                if dowhile and not cond(env):
                    return
        return run

    def stmt(self, n):
        if n is None or isinstance(n, c_ast.EmptyStatement):
            return lambda env: None
        if isinstance(n, c_ast.Compound):
            return self.block(n)
        if isinstance(n, c_ast.Decl):
            if n.init is None:
                return lambda env: None
            return self.assign(c_ast.ID(n.name), self.expr(n.init))
        if isinstance(n, c_ast.If):
            c = self.cond(n.cond)
            t = self.stmt(n.iftrue)
            f = self.stmt(n.iffalse)
            return lambda env: t(env) if c(env) else f(env)
        if isinstance(n, (c_ast.While, c_ast.DoWhile)):
            return self.loop(n)
        if isinstance(n, c_ast.For):
            init = self.expr(n.init)[1] if n.init is not None else None
            lp = self.loop(n)

            def run(env):
                if init:
                    init(env)
                lp(env)
            return run
        if isinstance(n, c_ast.Label):
            return self.stmt(n.stmt)
        if isinstance(n, c_ast.Goto):
            name = n.name

            def g(env):
                raise Goto(name)
            return g
        if isinstance(n, c_ast.Return):
            if n.expr is None:
                def r(env):
                    raise Ret(0)
                return r
            e = self.expr(n.expr)[1]

            def r(env):
                raise Ret(e(env))
            return r
        if isinstance(n, c_ast.Break):
            def b(env):
                raise Brk()
            return b
        if isinstance(n, c_ast.Continue):
            def c_(env):
                raise Cont()
            return c_
        if isinstance(n, c_ast.Switch):
            v = self.expr(n.cond)[1]
            cases = []
            for it in n.stmt.block_items or []:
                if isinstance(it, c_ast.Case):
                    cases.append((self.expr(it.expr)[1], [self.stmt(s) for s in it.stmts or []]))
                elif isinstance(it, c_ast.Default):
                    cases.append((None, [self.stmt(s) for s in it.stmts or []]))

            def sw(env):
                x = v(env)
                go = False
                try:
                    for ce, ss in cases:
                        go = go or ce is None or ce(env) == x
                        if go:
                            for s in ss:
                                s(env)
                except Brk:
                    pass
            return sw
        t, e = self.expr(n)
        return e

    # --- expressions: (type, fn(env) -> value) ---
    def cond(self, e):
        t, f = self.expr(e)
        return lambda env: f(env) != 0

    @staticmethod
    def sized_by_access(name):
        return (name.startswith('_') or 'Ram' in name) and GLOBAL_RE.match(name) is not None \
            and name not in ()

    def var(self, name):
        """(type, load fn, store fn, address fn or None)"""
        M = self.M
        if name in self.slots:
            i, t = self.slots[name]
            if t[0] == 'fn':
                t = U64

            def st(env, v):
                env[i] = v
            return t, (lambda env: env[i]), st, None
        if name in self.mems:
            o, t = self.mems[name]
            addr = lambda env: env[-1] - o
        elif GLOBAL_RE.match(name):
            a = gaddr(name)
            t = self.f.gtypes.get(name) or (U64 if self.sized_by_access(name) else self.M.gsym.get(a, U64))
            addr = lambda env: a
        else:
            raise NameError(f'{name} in {self.f.va:X}')
        if t[0] == 'a':
            return decay(t), addr, None, addr
        ld, sto = M.mk_load(t), M.mk_store(t)
        return t, (lambda env: ld(addr(env))), (lambda env, v: sto(addr(env), v)), addr

    def lvalue(self, e):
        """(type, load, store, addr)"""
        M = self.M
        if isinstance(e, c_ast.ID):
            return self.var(e.name)
        if isinstance(e, c_ast.StructRef) and e.type == '.':
            # Ghidra's partial access: v._N_M_ is M bytes of v starting at byte N
            import re
            m = re.fullmatch(r'_(\d+)_(\d+)_', e.field.name)
            if not m:
                raise NotImplementedError(f'field {e.field.name} in {self.f.va:X}')
            k, n = int(m.group(1)), int(m.group(2))
            bt, bld, bst, baddr = self.lvalue(e.name)
            t = ('i', n, False)
            mask, sh = (1 << (8 * n)) - 1, 8 * k
            if baddr is not None:
                addr = lambda env: baddr(env) + k
                ld, sto = M.mk_load(t), M.mk_store(t)
                return t, (lambda env: ld(addr(env))), (lambda env, v: sto(addr(env), v)), addr
            bw = wrapper_for(bt)

            def st(env, v):
                bst(env, bw((bld(env) & ~(mask << sh)) | ((v & mask) << sh)))
            return t, (lambda env: (bld(env) >> sh) & mask), st, None
        if isinstance(e, c_ast.Cast):
            return self.lvalue(e.expr)
        if isinstance(e, c_ast.UnaryOp) and e.op == '*':
            pt, pf = self.expr(e.expr)
            t = pt[1] if pt[0] == 'p' else U8
            if t[0] == 'v':
                t = U8
            addr = pf
        elif isinstance(e, c_ast.ArrayRef):
            bt, bf = self.expr(e.name)
            it, idx = self.expr(e.subscript)
            t = bt[1] if bt[0] == 'p' else U8
            if t[0] == 'v':
                t = U8
            es = sizeof(t)
            addr = lambda env: (bf(env) + idx(env) * es) & 0xFFFFFFFFFFFFFFFF
        else:
            raise NotImplementedError(f'lvalue {type(e).__name__}')
        if t[0] == 'a':
            return decay(t), addr, None, addr
        ld, sto = M.mk_load(t), M.mk_store(t)
        return t, (lambda env: ld(addr(env))), (lambda env, v: sto(addr(env), v)), addr

    def assign(self, lv, rhs):
        rt, rf = rhs
        if isinstance(lv, c_ast.ID) and self.sized_by_access(lv.name) and lv.name not in self.f.decl_globals:
            # `_DAT_x` / `uRam…`: Ghidra's access is wider (or narrower) than the symbol recorded at that address;
            # its size is that of the value stored
            self.f.gtypes[lv.name] = decay(rt) if rt[0] != 'fn' else U64
        t, ld, st, _ = self.lvalue(lv)
        w = wrapper_for(t)
        if t[0] == 'f':
            def a(env):
                v = float(rf(env))
                st(env, v)
                return v
        else:
            conv = (lambda v: int(v)) if rt[0] == 'f' else (lambda v: v)

            def a(env):
                v = w(conv(rf(env)))
                st(env, v)
                return v
        return a

    def expr(self, e):
        M = self.M
        if isinstance(e, c_ast.Constant):
            return self.const(e)
        if isinstance(e, c_ast.ID):
            n = e.name
            if n.startswith(('FUN_', 'LAB_', 'thunk_FUN_')):
                v = int(n.split('_')[-1], 16)
                return ('fn', U64), lambda env: v
            if n in ('true', 'false'):
                v = 1 if n == 'true' else 0
                return U8, lambda env: v
            t, ld, _, _ = self.var(n)
            return t, ld
        if isinstance(e, c_ast.Cast):
            t, f = self.expr(e.expr)
            to = ctype(e.to_type)
            if to[0] == 'f':
                return to, lambda env: float(f(env))
            w = wrapper_for(to)
            if t[0] == 'f':
                return to, lambda env: w(int(f(env)))
            return to, lambda env: w(f(env))
        if isinstance(e, c_ast.Assignment):
            if e.op == '=':
                t = self.lvalue(e.lvalue)[0]
                return t, self.assign(e.lvalue, self.expr(e.rvalue))
            t = self.lvalue(e.lvalue)[0]
            r = self.arith(e.op[:-1], self.expr(e.lvalue), self.expr(e.rvalue))
            return t, self.assign(e.lvalue, r)
        if isinstance(e, (c_ast.ArrayRef, c_ast.StructRef)):
            t, ld, _, _ = self.lvalue(e)
            return t, ld
        if isinstance(e, c_ast.UnaryOp):
            return self.unary(e)
        if isinstance(e, c_ast.BinaryOp):
            return self.binary(e)
        if isinstance(e, c_ast.FuncCall):
            return self.funccall(e)
        if isinstance(e, c_ast.TernaryOp):
            c = self.cond(e.cond)
            tt, tf = self.expr(e.iftrue)
            ft, ff = self.expr(e.iffalse)
            return tt, lambda env: tf(env) if c(env) else ff(env)
        if isinstance(e, c_ast.ExprList):
            fs = [self.expr(x) for x in e.exprs]

            def run(env):
                r = 0
                for _, f in fs:
                    r = f(env)
                return r
            return fs[-1][0], run
        raise NotImplementedError(f'expr {type(e).__name__}')

    def const(self, e):
        if e.type == 'string':
            s = bytes(e.value[1:-1], 'latin-1').decode('unicode_escape').encode('latin-1') + b'\0'
            a = self.M.cstring(s)
            return ptr(I8), lambda env: a
        if e.type == 'char':
            v = ord(bytes(e.value[1:-1], 'latin-1').decode('unicode_escape'))
            return I8, lambda env: v
        v = e.value.lower()
        if e.type in ('float', 'double'):
            x = float(v.rstrip('f'))
            return ('f', 4 if v.endswith('f') else 8), lambda env: x
        unsigned = 'u' in v
        n = int(v.rstrip('ul'), 0)
        if n < (1 << 31) and not unsigned:
            t = I32
        elif n < (1 << 32):
            t = ('i', 4, False) if unsigned or n >= (1 << 31) else I32
        else:
            t = U64 if unsigned or n >= (1 << 63) else I64
        return t, lambda env: n

    def unary(self, e):
        op = e.op
        if op == '*':
            t, ld, _, _ = self.lvalue(e)
            return t, ld
        if op == '&':
            if isinstance(e.expr, c_ast.ID) and e.expr.name.startswith(('FUN_', 'LAB_')):
                v = int(e.expr.name.split('_')[-1], 16)
                return ('fn', U64), lambda env: v
            if isinstance(e.expr, c_ast.ID) and e.expr.name in self.mems and self.mems[e.expr.name][1][0] == 'a':
                o, t = self.mems[e.expr.name]
                return ptr(t), lambda env: env[-1] - o
            t, _, _, addr = self.lvalue(e.expr)
            if addr is None:
                raise NotImplementedError(f'& of a register local in {self.f.va:X}')
            return ptr(t), addr
        if op == 'sizeof':
            n = sizeof(ctype(e.expr) if isinstance(e.expr, c_ast.Typename) else self.expr(e.expr)[0])
            return U64, lambda env: n
        if op in ('p++', 'p--', '++', '--'):
            t, ld, st, _ = self.lvalue(e.expr)
            step = (sizeof(t[1]) if t[0] == 'p' else 1) * (1 if '+' in op else -1)
            w = wrapper_for(t)
            post = op.startswith('p')

            def inc(env):
                old = ld(env)
                new = w(old + step)
                st(env, new)
                return old if post else new
            return t, inc
        t, f = self.expr(e.expr)
        if op == '-':
            if t[0] == 'f':
                return t, lambda env: -f(env)
            t = promote(decay(t))
            w = wrapper_for(t)
            return t, lambda env: w(-f(env))
        if op == '~':
            t = promote(t)
            w = wrapper_for(t)
            return t, lambda env: w(~f(env))
        if op == '!':
            return I32, lambda env: 0 if f(env) else 1
        if op == '+':
            return t, f
        raise NotImplementedError(op)

    def arith(self, op, x, y):
        (xt, xf), (yt, yf) = x, y
        xt, yt = decay(xt), decay(yt)
        if op in ('+', '-') and isptr(xt) and yt[0] == 'i':
            es = sizeof(xt[1]) if xt[0] == 'p' else 1
            s = es if op == '+' else -es
            return xt, lambda env: (xf(env) + yf(env) * s) & 0xFFFFFFFFFFFFFFFF
        if op == '+' and xt[0] == 'i' and isptr(yt):
            es = sizeof(yt[1])
            return yt, lambda env: (yf(env) + xf(env) * es) & 0xFFFFFFFFFFFFFFFF
        if op == '-' and isptr(xt) and isptr(yt):
            es = sizeof(xt[1])
            w = wrapper_for(I64)
            return I64, lambda env: w(xf(env) - yf(env)) // es
        if isptr(xt):
            xt = U64
        if isptr(yt):
            yt = U64
        if op in ('<<', '>>'):
            t = promote(xt)
            w = wrapper_for(t)
            mask = 63 if t[1] == 8 else 31
            if op == '<<':
                return t, lambda env: w(xf(env) << (yf(env) & mask))
            return t, lambda env: w(w(xf(env)) >> (yf(env) & mask))
        t = common(xt, yt)
        if t[0] == 'f':
            ops = {'+': lambda a, b: a + b, '-': lambda a, b: a - b, '*': lambda a, b: a * b, '/': lambda a, b: a / b}
            o = ops[op]
            return t, lambda env: o(float(xf(env)), float(yf(env)))
        w = wrapper_for(t)
        if op == '+':
            return t, lambda env: w(xf(env) + yf(env))
        if op == '-':
            return t, lambda env: w(xf(env) - yf(env))
        if op == '*':
            return t, lambda env: w(w(xf(env)) * w(yf(env)))
        if op == '&':
            return t, lambda env: w(xf(env) & yf(env))
        if op == '|':
            return t, lambda env: w(xf(env) | yf(env))
        if op == '^':
            return t, lambda env: w(xf(env) ^ yf(env))
        if op == '/':
            if t[2]:
                return t, lambda env: w(int(w(xf(env)) / w(yf(env))))
            return t, lambda env: w(xf(env)) // w(yf(env))
        if op == '%':
            if t[2]:
                return t, lambda env: (lambda a, b: w(a - int(a / b) * b))(w(xf(env)), w(yf(env)))
            return t, lambda env: w(xf(env)) % w(yf(env))
        raise NotImplementedError(op)

    def binary(self, e):
        op = e.op
        if op == '&&':
            a, b = self.cond(e.left), self.cond(e.right)
            return I32, lambda env: 1 if a(env) and b(env) else 0
        if op == '||':
            a, b = self.cond(e.left), self.cond(e.right)
            return I32, lambda env: 1 if a(env) or b(env) else 0
        x, y = self.expr(e.left), self.expr(e.right)
        if op in ('==', '!=', '<', '>', '<=', '>='):
            (xt, xf), (yt, yf) = x, y
            t = U64 if isptr(xt) or isptr(yt) else common(xt, yt)
            w = wrapper_for(t) if t[0] == 'i' else (lambda v: v)
            import operator
            o = {'==': operator.eq, '!=': operator.ne, '<': operator.lt, '>': operator.gt, '<=': operator.le,
                 '>=': operator.ge}[op]
            return I32, lambda env: 1 if o(w(xf(env)), w(yf(env))) else 0
        return self.arith(op, x, y)

    def funccall(self, e):
        M = self.M
        name = e.name
        args = [self.expr(a) for a in (e.args.exprs if e.args else [])]
        afs = [f for _, f in args]
        if isinstance(name, c_ast.ID) and name.name in ('memset', 'memcpy', 'memmove'):
            mem = M.mem
            d, s, n = afs
            if name.name == 'memset':
                def ms(env):
                    a, v, k = d(env), s(env), n(env)
                    mem.write(a, bytes([v & 0xFF]) * k)
                    return a
                return ptr(VOID), ms

            def mc(env):
                a, b, k = d(env), s(env), n(env)
                mem.write(a, mem.read(b, k))
                return a
            return ptr(VOID), mc
        if isinstance(name, c_ast.ID):
            op = ghidra_op(name.name, afs, args)
            if op is not None:
                return op
        tt, tf = self.expr(name)
        target = None
        if isinstance(name, c_ast.ID) and name.name.startswith(('FUN_', 'thunk_FUN_')):
            target = int(name.name.split('_')[-1], 16)
        rt = U64
        if target is not None and target not in M.hooks and M.parsed(target) is not None:
            rt = M.parsed(target).ret
            if rt == VOID or rt[0] == 'fn':
                rt = U64
        conv = [(lambda v: int(v) if isinstance(v, float) else v) for _ in afs]

        def call(env):
            vals = [c(f(env)) for c, f in zip(conv, afs)]
            return M.call(tf(env), vals)
        return rt, call
