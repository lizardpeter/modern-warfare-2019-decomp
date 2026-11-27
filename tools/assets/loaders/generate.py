#!/usr/bin/env python3
"""Generate the zone reader's Python source from the decompiled loaders (docs/assets/loader-translation.md).

    python3 tools/assets/loaders/generate.py     -> analysis/ModernWarfare_TU67/assets/loaders_gen.py

The same typed reading of Ghidra's C as compiler.py (which compiles to closures at run time and is the reference the
output is checked against), written out once as source. Every function reachable from Load_XAssetList and the stream
init is generated; calls to the stand-ins (stand_ins.py) go through a hook table. Functions with no `goto`, `switch`
or `continue` become structured Python; the others a block-by-block state machine, so C's jumps keep their meaning.
"""
import re
import sys
from pathlib import Path

from pycparser import c_ast

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stand_ins as S  # noqa: E402
from c_model import Func, ctype, sizeof, ptr, GLOBAL_RE, gaddr, I8, I32, I64, U8, U64, VOID  # noqa: E402
from compiler import promote, common, decay, isptr  # noqa: E402
from source import pseudocode, recorded_types  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'analysis' / 'ModernWarfare_TU67' / 'assets' / 'loaders_gen.py'
M64 = 0xFFFFFFFFFFFFFFFF


def W(t, code):
    """Code wrapping an integer expression to type t (as compiler.wrapper_for)."""
    if t[0] == 'i':
        if t[2]:
            return f'_s({code}, {8 * t[1]})'
        return f'(({code}) & {hex((1 << (8 * t[1])) - 1)})'
    if t[0] in ('p', 'fn'):
        return f'(({code}) & {hex(M64)})'
    if t[0] == 'f':
        return f'float({code})'
    return code


def ld(t, a):
    if t[0] == 'i':
        return f'_ld({a}, {t[1]}, {t[2]})'
    if t[0] in ('p', 'fn'):
        return f'_ld({a}, 8, False)'
    if t[0] == 'f':
        return f'_ldf({a}, {t[1]})'
    if t[0] == 'v':
        return f'_ld({a}, 1, False)'
    raise TypeError(t)


def st(t, a, v):
    if t[0] == 'i':
        return f'_st({a}, {t[1]}, {v})'
    if t[0] in ('p', 'fn'):
        return f'_st({a}, 8, {v})'
    if t[0] == 'f':
        return f'_stf({a}, {t[1]}, {v})'
    if t[0] == 'v':
        return f'_st({a}, 1, {v})'
    raise TypeError(t)


class Gen:
    """One function."""

    def __init__(self, f: Func, G):
        self.f, self.G = f, G
        self.tmp = 0
        addr_taken = set()

        def scan(n):
            if isinstance(n, c_ast.UnaryOp) and n.op == '&' and isinstance(n.expr, c_ast.ID):
                addr_taken.add(n.expr.name)
            for _, ch in n.children():
                scan(ch)
        scan(f.fd.body)
        self.slots, self.mems, off = {}, {}, 0
        for name, t in f.params + list(f.locals.items()):
            if name in addr_taken or t[0] == 'a':
                off += (sizeof(t) + 15) & ~15
                self.mems[name] = (off, t)
            else:
                self.slots[name] = t
        self.frame_size = off + 0x40
        flat = False

        def hard(n):
            nonlocal flat
            if isinstance(n, (c_ast.Goto, c_ast.Switch, c_ast.Continue)):
                flat = True
            for _, ch in n.children():
                hard(ch)
        hard(f.fd.body)
        self.flat = flat

    def t(self):
        self.tmp += 1
        return f'_t{self.tmp}'

    # ---------------- variables ----------------
    @staticmethod
    def sized_by_access(name):
        return (name.startswith('_') or 'Ram' in name) and GLOBAL_RE.match(name) is not None

    def var(self, name):
        """(type, load code, store fn(code)->stmt code, addr code or None, slot name or None)"""
        if name in self.slots:
            t = self.slots[name]
            if t[0] == 'fn':
                t = U64
            v = 'v_' + name
            return t, v, (lambda c: f'{v} = {c}'), None, v
        if name in self.mems:
            o, t = self.mems[name]
            addr = f'(fb - {o})'
        elif GLOBAL_RE.match(name):
            a = gaddr(name)
            t = self.f.gtypes.get(name) or (U64 if self.sized_by_access(name) else self.G.recorded.get(a, U64))
            addr = hex(a)
        else:
            raise NameError(f'{name} in {self.f.va:X}')
        if t[0] == 'a':
            return decay(t), addr, None, addr, None
        return t, ld(t, addr), (lambda c, t=t, addr=addr: st(t, addr, c)), addr, None

    def lvalue(self, e):
        if isinstance(e, c_ast.ID):
            return self.var(e.name)
        if isinstance(e, c_ast.StructRef) and e.type == '.':
            m = re.fullmatch(r'_(\d+)_(\d+)_', e.field.name)
            if not m:
                raise NotImplementedError(f'field {e.field.name} in {self.f.va:X}')
            k, n = int(m.group(1)), int(m.group(2))
            bt, bld, bst, baddr, bslot = self.lvalue(e.name)
            t = ('i', n, False)
            mask, sh = (1 << (8 * n)) - 1, 8 * k
            if baddr is not None:
                addr = f'({baddr} + {k})'
                return t, ld(t, addr), (lambda c: st(t, addr, c)), addr, None
            load = f'(({bld} >> {sh}) & {hex(mask)})'
            return t, load, (lambda c: bst(W(bt, f'({bld} & {hex(~(mask << sh) & ((1 << 80) - 1))}) | '
                                                 f'((({c}) & {hex(mask)}) << {sh})'))), None, None
        if isinstance(e, c_ast.Cast):
            return self.lvalue(e.expr)
        if isinstance(e, c_ast.UnaryOp) and e.op == '*':
            pt, pc = self.expr(e.expr)
            t = pt[1] if pt[0] == 'p' else U8
            if t[0] == 'v':
                t = U8
            addr = pc
        elif isinstance(e, c_ast.ArrayRef):
            bt, bc = self.expr(e.name)
            it, ic = self.expr(e.subscript)
            t = bt[1] if bt[0] == 'p' else U8
            if t[0] == 'v':
                t = U8
            addr = f'(({bc} + ({ic}) * {sizeof(t)}) & {hex(M64)})'
        else:
            raise NotImplementedError(f'lvalue {type(e).__name__}')
        if t[0] == 'a':
            return decay(t), addr, None, addr, None
        if not re.fullmatch(r'[\w.()+\- ]*', addr) or len(addr) > 40:
            # evaluate the address once
            a = self.t()
            return t, ld(t, a), (lambda c, a=a: st(t, a, c)), a, ('addr', a, addr)
        return t, ld(t, addr), (lambda c: st(t, addr, c)), addr, None

    # ---------------- expressions: (type, code) ----------------
    def assign_code(self, lv, rhs, as_expr):
        """Assignment; returns (type, statement lines, value expression or None)."""
        rt, rc = rhs
        if isinstance(lv, c_ast.ID) and self.sized_by_access(lv.name) and lv.name not in self.f.decl_globals:
            self.f.gtypes[lv.name] = decay(rt) if rt[0] != 'fn' else U64
        t, load, store, addr, extra = self.lvalue(lv)
        if t[0] == 'f':
            val = f'float({rc})'
        else:
            val = W(t, f'int({rc})' if rt[0] == 'f' else rc)
        pre = []
        if isinstance(extra, tuple) and extra[0] == 'addr':
            pre.append(f'{extra[1]} = {extra[2]}')
        v = self.t()
        lines = pre + [f'{v} = {val}', store(v)]
        return t, lines, v

    def expr(self, e):
        """(type, code). Side effects inside expressions use helper calls or walrus temporaries."""
        if isinstance(e, c_ast.Constant):
            return self.const(e)
        if isinstance(e, c_ast.ID):
            n = e.name
            if n.startswith(('FUN_', 'LAB_', 'thunk_FUN_')):
                return ('fn', U64), hex(int(n.split('_')[-1], 16))
            if n in ('true', 'false'):
                return U8, '1' if n == 'true' else '0'
            t, load, _, _, _ = self.var(n)
            return t, load
        if isinstance(e, c_ast.Cast):
            t, c = self.expr(e.expr)
            to = ctype(e.to_type)
            if to[0] == 'f':
                return to, f'float({c})'
            return to, W(to, f'int({c})' if t[0] == 'f' else c)
        if isinstance(e, c_ast.Assignment):
            if e.op == '=':
                t, lines, v = self.assign_code(e.lvalue, self.expr(e.rvalue), True)
            else:
                t0 = self.lvalue(e.lvalue)[0]
                r = self.arith(e.op[:-1], self.expr(e.lvalue), self.expr(e.rvalue))
                t, lines, v = self.assign_code(e.lvalue, r, True)
                t = t0
            return t, self.inline(lines, v)
        if isinstance(e, (c_ast.ArrayRef, c_ast.StructRef)):
            t, load, _, _, extra = self.lvalue(e)
            if isinstance(extra, tuple) and extra[0] == 'addr':
                return t, f'(({extra[1]} := {extra[2]}), {load})[1]'
            return t, load
        if isinstance(e, c_ast.UnaryOp):
            return self.unary(e)
        if isinstance(e, c_ast.BinaryOp):
            return self.binary(e)
        if isinstance(e, c_ast.FuncCall):
            return self.funccall(e)
        if isinstance(e, c_ast.TernaryOp):
            c = self.cond(e.cond)
            tt, tc = self.expr(e.iftrue)
            ft, fc = self.expr(e.iffalse)
            return tt, f'(({tc}) if {c} else ({fc}))'
        if isinstance(e, c_ast.ExprList):
            parts = [self.expr(x) for x in e.exprs]
            return parts[-1][0], '(' + ', '.join(c for _, c in parts) + ')[-1]'
        raise NotImplementedError(f'expr {type(e).__name__} in {self.f.va:X}')

    @staticmethod
    def inline(lines, v):
        """Statement lines as one expression whose value is v: `(_t1 := …, _st(…), …)[k]`."""
        parts = []
        for ln in lines:
            m = re.fullmatch(r'(\w+) = (.*)', ln, re.S)
            parts.append(f'({m.group(1)} := {m.group(2)})' if m else ln)
        return '(' + ', '.join(parts) + f', {v})[-1]'

    def cond(self, e):
        t, c = self.expr(e)
        return f'(({c}) != 0)'

    def const(self, e):
        if e.type == 'string':
            s = bytes(e.value[1:-1], 'latin-1').decode('unicode_escape').encode('latin-1') + b'\0'
            return ptr(I8), f'R.cstring({s!r})'
        if e.type == 'char':
            return I8, str(ord(bytes(e.value[1:-1], 'latin-1').decode('unicode_escape')))
        v = e.value.lower()
        if e.type in ('float', 'double'):
            return ('f', 4 if v.endswith('f') else 8), repr(float(v.rstrip('f')))
        unsigned = 'u' in v
        n = int(v.rstrip('ul'), 0)
        if n < (1 << 31) and not unsigned:
            t = I32
        elif n < (1 << 32):
            t = ('i', 4, False) if unsigned or n >= (1 << 31) else I32
        else:
            t = U64 if unsigned or n >= (1 << 63) else I64
        return t, hex(n) if n > 9 else str(n)

    def unary(self, e):
        op = e.op
        if op == '*':
            t, load, _, _, extra = self.lvalue(e)
            if isinstance(extra, tuple) and extra[0] == 'addr':
                return t, f'(({extra[1]} := {extra[2]}), {load})[1]'
            return t, load
        if op == '&':
            if isinstance(e.expr, c_ast.ID) and e.expr.name.startswith(('FUN_', 'LAB_')):
                return ('fn', U64), hex(int(e.expr.name.split('_')[-1], 16))
            if isinstance(e.expr, c_ast.ID) and e.expr.name in self.mems and self.mems[e.expr.name][1][0] == 'a':
                o, t = self.mems[e.expr.name]
                return ptr(t), f'(fb - {o})'
            t, _, _, addr, extra = self.lvalue(e.expr)
            if addr is None:
                raise NotImplementedError(f'& of a register local in {self.f.va:X}')
            if isinstance(extra, tuple) and extra[0] == 'addr':
                return ptr(t), extra[2]
            return ptr(t), addr
        if op == 'sizeof':
            return U64, str(sizeof(ctype(e.expr) if isinstance(e.expr, c_ast.Typename) else self.expr(e.expr)[0]))
        if op in ('p++', 'p--', '++', '--'):
            t, load, store, addr, extra = self.lvalue(e.expr)
            step = (sizeof(t[1]) if t[0] == 'p' else 1) * (1 if '+' in op else -1)
            old, new = self.t(), self.t()
            lines = []
            if isinstance(extra, tuple) and extra[0] == 'addr':
                lines.append(f'{extra[1]} = {extra[2]}')
            lines += [f'{old} = {load}', f'{new} = {W(t, f"{old} + {step}")}', store(new)]
            return t, self.inline(lines, old if op.startswith('p') else new)
        t, c = self.expr(e.expr)
        if op == '-':
            if t[0] == 'f':
                return t, f'(-{c})'
            t = promote(decay(t))
            return t, W(t, f'-({c})')
        if op == '~':
            t = promote(t)
            return t, W(t, f'~({c})')
        if op == '!':
            return I32, f'(0 if ({c}) else 1)'
        if op == '+':
            return t, c
        raise NotImplementedError(op)

    def arith(self, op, x, y):
        (xt, xc), (yt, yc) = x, y
        xt, yt = decay(xt), decay(yt)
        if op in ('+', '-') and isptr(xt) and yt[0] == 'i':
            es = sizeof(xt[1]) if xt[0] == 'p' else 1
            s = es if op == '+' else -es
            return xt, f'(({xc} + ({yc}) * {s}) & {hex(M64)})'
        if op == '+' and xt[0] == 'i' and isptr(yt):
            return yt, f'(({yc} + ({xc}) * {sizeof(yt[1])}) & {hex(M64)})'
        if op == '-' and isptr(xt) and isptr(yt):
            return I64, f'({W(I64, f"{xc} - {yc}")} // {sizeof(xt[1])})'
        if isptr(xt):
            xt = U64
        if isptr(yt):
            yt = U64
        if op in ('<<', '>>'):
            t = promote(xt)
            mask = 63 if t[1] == 8 else 31
            if op == '<<':
                return t, W(t, f'({xc}) << (({yc}) & {mask})')
            return t, W(t, f'{W(t, xc)} >> (({yc}) & {mask})')
        t = common(xt, yt)
        if t[0] == 'f':
            return t, f'(float({xc}) {op} float({yc}))'
        if op in ('+', '-', '&', '|', '^'):
            return t, W(t, f'({xc}) {op} ({yc})')
        if op == '*':
            return t, W(t, f'{W(t, xc)} * {W(t, yc)}')
        if op == '/':
            if t[2]:
                return t, f'_sdiv({W(t, xc)}, {W(t, yc)}, {8 * t[1]})'
            return t, f'({W(t, xc)} // {W(t, yc)})'
        if op == '%':
            if t[2]:
                return t, f'_smod({W(t, xc)}, {W(t, yc)}, {8 * t[1]})'
            return t, f'({W(t, xc)} % {W(t, yc)})'
        raise NotImplementedError(op)

    def binary(self, e):
        op = e.op
        if op == '&&':
            return I32, f'(1 if ({self.cond(e.left)} and {self.cond(e.right)}) else 0)'
        if op == '||':
            return I32, f'(1 if ({self.cond(e.left)} or {self.cond(e.right)}) else 0)'
        x, y = self.expr(e.left), self.expr(e.right)
        if op in ('==', '!=', '<', '>', '<=', '>='):
            (xt, xc), (yt, yc) = x, y
            t = U64 if isptr(xt) or isptr(yt) else common(xt, yt)
            if t[0] == 'i':
                xc, yc = W(t, xc), W(t, yc)
            return I32, f'(1 if ({xc}) {op} ({yc}) else 0)'
        return self.arith(op, x, y)

    def funccall(self, e):
        name = e.name
        args = [self.expr(a) for a in (e.args.exprs if e.args else [])]
        acs = [c if t[0] != 'f' else f'int({c})' for t, c in args]
        if isinstance(name, c_ast.ID) and name.name in ('memset', 'memcpy', 'memmove'):
            d, s, n = [c for _, c in args]
            if name.name == 'memset':
                return ptr(VOID), f'_memset({d}, {s}, {n})'
            return ptr(VOID), f'_memcpy({d}, {s}, {n})'
        if isinstance(name, c_ast.ID) and name.name == 'POPCOUNT':
            return I32, f"bin(({args[0][1]}) & {hex(M64)}).count('1')"
        if isinstance(name, c_ast.ID):
            m = re.fullmatch(r'(CONCAT|SUB|ZEXT|SEXT)(\d)(\d+)', name.name)
            if m:
                kind, x, y = m.group(1), int(m.group(2)), int(m.group(3))
                cs = [c for _, c in args]
                if kind == 'CONCAT':
                    return ('i', x + y, False), (f'(((({cs[0]}) & {hex((1 << (8 * x)) - 1)}) << {8 * y}) | '
                                                 f'(({cs[1]}) & {hex((1 << (8 * y)) - 1)}))')
                if kind == 'SUB':
                    return ('i', y, False), f'((({cs[0]}) >> (8 * ({cs[1]}))) & {hex((1 << (8 * y)) - 1)})'
                if kind == 'ZEXT':
                    return ('i', y, False), f'(({cs[0]}) & {hex((1 << (8 * x)) - 1)})'
                h = 1 << (8 * x - 1)
                return ('i', y, True), W(('i', y, True), f'((({cs[0]}) & {hex((1 << (8 * x)) - 1)}) ^ {hex(h)}) - {hex(h)}')
        target = None
        if isinstance(name, c_ast.ID) and name.name.startswith(('FUN_', 'thunk_FUN_')):
            target = int(name.name.split('_')[-1], 16)
        rt = U64
        if target is not None and target not in self.G.hooked and self.G.parsed(target) is not None:
            rt = self.G.parsed(target).ret
            if rt == VOID or rt[0] == 'fn':
                rt = U64
        argl = '[' + ', '.join(acs) + ']'
        if target is not None:
            self.G.want(target)
            if target in self.G.hooked:
                return rt, f'H[{hex(target)}](R, {argl})'
            if not self.G.translated(target):
                return rt, f'R.untranslated({hex(target)})'
            return rt, f'F_{target:X}({", ".join(acs)})'
        tt, tc = self.expr(name)
        return rt, f'R.call({tc}, {argl})'

    # ---------------- statements ----------------
    def lines_of_expr_stmt(self, e):
        if isinstance(e, c_ast.Assignment):
            if e.op == '=':
                _, lines, _ = self.assign_code(e.lvalue, self.expr(e.rvalue), False)
            else:
                r = self.arith(e.op[:-1], self.expr(e.lvalue), self.expr(e.rvalue))
                _, lines, _ = self.assign_code(e.lvalue, r, False)
            return lines
        t, c = self.expr(e)
        return [c]

    def emit_struct(self, n, ind, out):
        """Structured emission (no goto / switch / continue in the function)."""
        p = '    ' * ind
        if n is None or isinstance(n, c_ast.EmptyStatement):
            return
        if isinstance(n, c_ast.Compound):
            for it in n.block_items or []:
                self.emit_struct(it, ind, out)
            return
        if isinstance(n, c_ast.Decl):
            if n.init is not None:
                _, lines, _ = self.assign_code(c_ast.ID(n.name), self.expr(n.init), False)
                out += [p + ln for ln in lines]
            return
        if isinstance(n, c_ast.Label):
            return self.emit_struct(n.stmt, ind, out)
        if isinstance(n, c_ast.If):
            out.append(f'{p}if {self.cond(n.cond)}:')
            k = len(out)
            self.emit_struct(n.iftrue, ind + 1, out)
            if len(out) == k:
                out.append(p + '    pass')
            if n.iffalse is not None:
                out.append(f'{p}else:')
                k = len(out)
                self.emit_struct(n.iffalse, ind + 1, out)
                if len(out) == k:
                    out.append(p + '    pass')
            return
        if isinstance(n, (c_ast.While, c_ast.DoWhile, c_ast.For)):
            if isinstance(n, c_ast.For) and n.init is not None and not isinstance(n.init, c_ast.DeclList):
                out += [p + ln for ln in self.lines_of_expr_stmt(n.init)]
            out.append(f'{p}while True:')
            if not isinstance(n, c_ast.DoWhile) and n.cond is not None:
                out.append(f'{p}    if not {self.cond(n.cond)}:')
                out.append(f'{p}        break')
            self.emit_struct(n.stmt, ind + 1, out)
            if isinstance(n, c_ast.For) and n.next is not None:
                out += [p + '    ' + ln for ln in self.lines_of_expr_stmt(n.next)]
            if isinstance(n, c_ast.DoWhile):
                out.append(f'{p}    if not {self.cond(n.cond)}:')
                out.append(f'{p}        break')
            return
        if isinstance(n, c_ast.Return):
            if n.expr is None:
                out.append(f'{p}return 0')
            else:
                out.append(f'{p}return {self.expr(n.expr)[1]}')
            return
        if isinstance(n, c_ast.Break):
            out.append(f'{p}break')
            return
        out += [p + ln for ln in self.lines_of_expr_stmt(n)]

    # flattened: a list of basic statements with labels and jumps, run by a pc loop
    def lower(self, n, ops, brk=None, cont=None):
        def L():
            self.tmp += 1
            return f'L{self.tmp}'
        if n is None or isinstance(n, c_ast.EmptyStatement):
            return
        if isinstance(n, c_ast.Compound):
            for it in n.block_items or []:
                self.lower(it, ops, brk, cont)
            return
        if isinstance(n, c_ast.Decl):
            if n.init is not None:
                ops.append(('code', self.assign_code(c_ast.ID(n.name), self.expr(n.init), False)[1]))
            return
        if isinstance(n, c_ast.Label):
            ops.append(('label', 'G_' + n.name))
            return self.lower(n.stmt, ops, brk, cont)
        if isinstance(n, c_ast.Goto):
            ops.append(('jmp', 'G_' + n.name))
            return
        if isinstance(n, c_ast.If):
            els, end = L(), L()
            ops.append(('jz', self.cond(n.cond), els))
            self.lower(n.iftrue, ops, brk, cont)
            ops.append(('jmp', end))
            ops.append(('label', els))
            self.lower(n.iffalse, ops, brk, cont)
            ops.append(('label', end))
            return
        if isinstance(n, (c_ast.While, c_ast.For)):
            if isinstance(n, c_ast.For) and n.init is not None and not isinstance(n.init, c_ast.DeclList):
                ops.append(('code', self.lines_of_expr_stmt(n.init)))
            top, nxt, end = L(), L(), L()
            ops.append(('label', top))
            if n.cond is not None:
                ops.append(('jz', self.cond(n.cond), end))
            self.lower(n.stmt, ops, end, nxt)
            ops.append(('label', nxt))
            if isinstance(n, c_ast.For) and n.next is not None:
                ops.append(('code', self.lines_of_expr_stmt(n.next)))
            ops.append(('jmp', top))
            ops.append(('label', end))
            return
        if isinstance(n, c_ast.DoWhile):
            top, nxt, end = L(), L(), L()
            ops.append(('label', top))
            self.lower(n.stmt, ops, end, nxt)
            ops.append(('label', nxt))
            ops.append(('jnz', self.cond(n.cond), top))
            ops.append(('label', end))
            return
        if isinstance(n, c_ast.Switch):
            v = self.t()
            ops.append(('code', [f'{v} = {self.expr(n.cond)[1]}']))
            end = L()
            cases, default = [], None
            for it in n.stmt.block_items or []:
                lab = L()
                if isinstance(it, c_ast.Case):
                    cases.append((self.expr(it.expr)[1], lab, it))
                elif isinstance(it, c_ast.Default):
                    default = lab
                    cases.append((None, lab, it))
            for ce, lab, _ in cases:
                if ce is not None:
                    ops.append(('jnz', f'({v} == ({ce}))', lab))
            ops.append(('jmp', default or end))
            for _, lab, it in cases:
                ops.append(('label', lab))
                for s in it.stmts or []:
                    self.lower(s, ops, end, cont)
            ops.append(('label', end))
            return
        if isinstance(n, c_ast.Return):
            ops.append(('ret', '0' if n.expr is None else self.expr(n.expr)[1]))
            return
        if isinstance(n, c_ast.Break):
            ops.append(('jmp', brk))
            return
        if isinstance(n, c_ast.Continue):
            ops.append(('jmp', cont))
            return
        ops.append(('code', self.lines_of_expr_stmt(n)))

    def emit_flat(self, out):
        ops = []
        self.lower(self.f.fd.body, ops)
        # split into blocks at labels
        blocks, cur, names = [], [], {}
        for op in ops:
            if op[0] == 'label':
                blocks.append(cur)
                cur = []
                names[op[1]] = len(blocks)
            else:
                cur.append(op)
        blocks.append(cur)
        out.append('    pc = 0')
        out.append('    while True:')
        for i, b in enumerate(blocks):
            out.append(f'        {"if" if i == 0 else "elif"} pc == {i}:')
            ended = False
            for op in b:
                if ended:
                    break
                if op[0] == 'code':
                    out += ['            ' + ln for ln in op[1]]
                elif op[0] == 'jmp':
                    out.append(f'            pc = {names[op[1]]}')
                    out.append('            continue')
                    ended = True
                elif op[0] == 'jz':
                    out.append(f'            if not {op[1]}:')
                    out.append(f'                pc = {names[op[2]]}')
                    out.append('                continue')
                elif op[0] == 'jnz':
                    out.append(f'            if {op[1]}:')
                    out.append(f'                pc = {names[op[2]]}')
                    out.append('                continue')
                elif op[0] == 'ret':
                    out.append(f'            return {op[1]}')
                    ended = True
            if not ended:
                if i + 1 < len(blocks):
                    out.append(f'            pc = {i + 1}')
                else:
                    out.append('            return 0')

    def generate(self):
        f = self.f
        # C lets a call pass more arguments than the callee declares (they are ignored), and fewer (the rest read
        # as 0 here, as in compiler.py)
        params = ', '.join([f'a{i}=0' for i in range(len(f.params))] + ['*_'])
        out = [f'def F_{f.va:X}({params}):', '    fb = R.sp', f'    R.sp = fb - {self.frame_size}', '    try:']
        body = ['    ' + ln for ln in self._body()]
        out += ['    ' + ln for ln in body] if False else []
        prologue = []
        for i, (name, t) in enumerate(f.params):
            if name in self.slots:
                prologue.append(f'v_{name} = {W(t, f"a{i}") if t[0] != "f" else f"float(a{i})"}')
            else:
                o, tt = self.mems[name]
                prologue.append(st(tt, f'(fb - {o})', W(tt, f'a{i}') if tt[0] != 'f' else f'float(a{i})'))
        for name, t in self.slots.items():
            if name not in dict(f.params):
                prologue.append(f'v_{name} = 0')
        inner = prologue + self.body_lines
        out += ['        ' + ln for ln in inner]
        out.append('    finally:')
        out.append('        R.sp = fb')
        return out

    def _body(self):
        lines = []
        if self.flat:
            self.emit_flat(lines)
            lines = [ln[4:] for ln in lines]
        else:
            self.emit_struct(self.f.fd.body, 0, lines)
            lines.append('return 0')
        self.body_lines = [self._ret_wrap(ln) for ln in lines]
        return self.body_lines

    def _ret_wrap(self, ln):
        r = self.f.ret
        m = re.fullmatch(r'(\s*)return (.*)', ln)
        if m and r[0] in ('i', 'p'):
            return f'{m.group(1)}return {W(r, m.group(2))}'
        return ln


class Program:
    def __init__(self):
        self.src = pseudocode()
        self.recorded = recorded_types()
        self.hooked = {S.READ, S.ADD_ASSET, S.SL_GET_STRING, S.MEMCPY, *S.CANCEL_CHECKS, *S.SKIPPED, *S.WRAPPERS}
        self.cache, self.todo, self.done = {}, [], set()
        self.errors = {}

    def parsed(self, va):
        if va not in self.cache:
            t = self.src.get(va)
            try:
                self.cache[va] = Func(va, t) if t is not None else None
            except Exception:
                self.cache[va] = None
        return self.cache[va]

    def translated(self, va):
        return va in S.TRANSLATED_OUTSIDE or any(a <= va < b for a, b in S.TRANSLATED_RANGES)

    def want(self, va):
        if va not in self.done and va not in self.hooked and self.translated(va):
            self.done.add(va)
            self.todo.append(va)

    def run(self, roots):
        for r in roots:
            self.want(r)
        out, failed = [], []
        while self.todo:
            va = self.todo.pop()
            f = self.parsed(va)
            if f is None:
                failed.append(va)
                out.append(f'def F_{va:X}(*a):\n    raise RuntimeError("{va:X}: no usable pseudocode")\n')
                continue
            try:
                g = Gen(f, self)
                g._body()
                out.append('\n'.join(g.generate()) + '\n')
            except Exception as e:
                failed.append(va)
                self.errors[va] = f'{type(e).__name__}: {e}'
                out.append(f'def F_{va:X}(*a):\n    raise RuntimeError({f"{va:X}: not translated: {e}"!r})\n')
        return out, failed


HEADER = '''# GENERATED by tools/assets/loaders/generate.py from analysis/ModernWarfare_TU67/pseudocode — do not edit.
# TU67's zone loaders as Python (docs/assets/loader-translation.md). Bind with bind(runtime, hooks) first.
R = None
H = None
_ld = _st = _ldf = _stf = _memset = _memcpy = None


def _s(v, bits):
    v &= (1 << bits) - 1
    return v - (1 << bits) if v >> (bits - 1) else v


def _sdiv(a, b, bits):
    return _s(int(a / b), bits)


def _smod(a, b, bits):
    return _s(a - int(a / b) * b, bits)


def bind(runtime, hooks):
    global R, H, _ld, _st, _ldf, _stf, _memset, _memcpy
    R, H = runtime, hooks
    _ld, _st, _ldf, _stf = runtime.ld, runtime.st, runtime.ldf, runtime.stf
    _memset, _memcpy = runtime.memset, runtime.memcpy

'''


def main():
    p = Program()
    out, failed = p.run([S.LOAD_ASSET_LIST, S.INIT_STREAMS, S.RESET_TRACKERS])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = HEADER + '\n\n'.join(out) + '\n\nFUNCS = {' + ', '.join(
        f'{va:#x}: F_{va:X}' for va in sorted(p.done)) + '}\n'
    OUT.write_text(text)
    compile(text, str(OUT), 'exec')
    print(f'{len(out)} functions, {len(failed)} not translated, {len(text) // 1024} KiB -> {OUT}')
    import collections
    kinds = collections.Counter(re.sub(r' in [0-9A-F]{9}', '', e) for e in p.errors.values())
    for k, n in kinds.most_common():
        print(f'  {n:4d}  {k}')


if __name__ == '__main__':
    main()
