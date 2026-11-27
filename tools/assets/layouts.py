#!/usr/bin/env python3
"""Asset layouts from the game's own loaders: every struct each asset type is made of (docs/assets/layouts.md).

    python3 tools/assets/layouts.py <zone.ff>[:<zone.fp>[:<decompressed>]] ... [--oodle <oo2core_7_win64.dll>]

Loads each zone with the generated reader (tools/assets/loaders) while recording every call to Load_Stream
143760AE0. Every loader passes it the address and size of the struct it fills, also when the data was already read
(flag 1), so the calls list every struct instance: its loader, address and size. From the loaded memory:

- a struct loader is one whose Load_Stream size never varies; that size is the struct's size;
- a field is a pointer to X when its value is the start of an instance or array X loaded by another loader, a
  string when it points at text, an asset reference when it holds an asset's header address;
- a count field is a header field (u8/u16/u32) equal on every instance to the number of elements the pointer
  leads to, for some element size;
- a script-string field is one passed to Load_ScriptString 143760D10.

Instances in the temporary block are taken from the pool copy DB_AddXAsset made of their asset, since the block is
reused. Writes analysis/ModernWarfare_TU67/assets/layouts.tsv and layouts/<type>.md (generated).
"""
import argparse
import bisect
import collections
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'assets'))
sys.path.insert(0, str(ROOT / 'tools' / 'assets' / 'loaders'))
import stand_ins as S  # noqa: E402
import zone  # noqa: E402
from load import ZoneLoad  # noqa: E402

OUT = ROOT / 'analysis' / 'ModernWarfare_TU67' / 'assets'
LOAD_STREAM, LOAD_SCRIPT_STRING = 0x143760AE0, 0x143760D10
PRIMITIVES = {LOAD_STREAM, 0x1437606D0, 0x143760620, 0x142DF1380, 0x142DF1930, 0x142DF1700, 0x142DF2230,
              0x142DF1F60, 0x1437604F0, 0x142DFEF30, 0x142DFEFA0, LOAD_SCRIPT_STRING, 0x143760BC0, 0x143760B30}
ELEMENT_SIZES = (1, 2, 4, 8, 0xC, 0x10, 0x14, 0x18, 0x20, 0x28, 0x30, 0x40)


def trace(data, header):
    """Load a zone, recording (loader, address, size, flag) for every Load_Stream call and the script-string fields."""
    z = ZoneLoad(data, header)
    mod = next(iter(z.machine.funcs.values())).__globals__
    stack, visits, sfields, adds = [], [], [], []
    last_struct = {}     # loader -> index of its latest struct visit

    def innermost():
        return next((v for v in reversed(stack) if v not in PRIMITIVES), None)
    for name, f in list(mod.items()):
        if not (name.startswith('F_') and callable(f)):
            continue
        va = int(name[2:], 16)
        if va == LOAD_STREAM:
            def w(a0=0, a1=0, a2=0, *_, f=f):
                # the call site: the generated line, one per Load_Stream call in the C (site_element() reads it)
                # frame 2: the generated code (frame 1 is link(), which wraps this)
                site = (innermost(), sys._getframe(2).f_lineno)
                if site_constant(site):
                    last_struct[site[0]] = len(visits)
                visits.append((site, a1, a2, a0))
                return f(a0, a1, a2)
        elif va == LOAD_SCRIPT_STRING:
            def w(a0=0, *r, f=f):
                sfields.append((innermost(), a0, len(visits)))
                return f(a0, *r)
        else:
            def w(*a, f=f, va=va):
                stack.append(va)
                try:
                    return f(*a)
                finally:
                    stack.pop()
        mod[name] = w
    # the loaders set a pointer field to the stream position just before the child reads there
    # (`field = pos; Load_Child(...)`): link each read to the struct field that last received its address
    last_store = {}
    links = []          # (visit index of the read, field address)
    st = mod['_st']

    def store(a, n, v, st=st):
        # only stores into zone memory: the code also copies the position into a global ("current child")
        if n == 8 and a >= S.POOL:
            last_store[v] = a
        return st(a, n, v)
    mod['_st'] = store
    lsw = mod['F_143760AE0']

    def link(a0=0, a1=0, a2=0, *r, f=lsw):
        if a0 != 1 and a2:
            fa = last_store.get(a1)
            if fa is not None:
                # the parent: the latest struct instance, of a loader on the call stack, that contains the field
                for L in reversed(stack):
                    j = last_struct.get(L)
                    if j is not None:
                        site, a, n, flag = visits[j]
                        if a <= fa < a + site_constant(site):
                            links.append((len(visits), j, fa))
                            break
        return f(a0, a1, a2, *r)
    mod['F_143760AE0'] = link
    orig = z._copy

    def copy(typ, hdr):
        c = orig(typ, hdr)
        adds.append((len(visits), hdr, z.types[typ][1], c))
        return c
    z._copy = copy
    z.load()
    z.links = links
    return z, visits, sfields, adds


_GEN = None


def site_constant(site):
    """The struct size when the call site reads a size written as a constant in the code (a struct read); None when
    the size is computed (an array read)."""
    import re
    global _GEN
    if _GEN is None:
        _GEN = (OUT / 'loaders_gen.py').read_text().splitlines()
    line = _GEN[site[1] - 1] if site and site[1] and site[1] <= len(_GEN) else ''
    m = re.search(r'F_143760AE0\(.*, (0x[0-9a-f]+|\d+)\)\s*$', line)
    return int(m.group(1), 0) if m else None


def site_element(site):
    """For a call site whose read size varies: the element size, from the size expression on its generated line
    (`count * K`, `count << n`, or `count` for bytes)."""
    import re
    global _GEN
    if _GEN is None:
        _GEN = (OUT / 'loaders_gen.py').read_text().splitlines()
    line = _GEN[site[1] - 1] if site and site[1] and site[1] <= len(_GEN) else ''
    m = re.search(r'<< \(\((\d+)\) & 63\)', line)
    if m:
        return 1 << int(m.group(1))
    # the multiplier as generate.py writes it: signed `_s(count, 64) * _s(K, 64)`, unsigned
    # `((count) & mask) * ((K) & mask)`, or plain `count * K`
    for pat in (r'\* _s\((0x[0-9a-f]+|\d+), \d+\)', r'\* \(\((0x[0-9a-f]+|\d+)\) &', r'\* (0x[0-9a-f]+|\d+)\)'):
        m = re.search(pat, line)
        if m:
            return int(m.group(1), 0)
    return 1


class Evidence:
    """Observations merged over every zone traced."""

    def __init__(self):
        self.sizes = collections.defaultdict(collections.Counter)    # loader -> {size: visits}
        self.instances = collections.Counter()                       # struct loader -> instances seen
        self.fields = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
        self.count_obs = collections.defaultdict(list)               # (loader, off) -> [(values at offsets, n bytes)]
        self.sstr = collections.defaultdict(collections.Counter)     # loader -> {offset: times}
        self.bodies = {}                                             # (zone, instance address) -> bytes
        self.zone = 0

    def add_zone(self, z, visits, sfields, adds):
        mem = z.mem
        q = lambda a: struct.unpack('<Q', mem.read(a, 8))[0]   # noqa: E731
        sizes = collections.defaultdict(collections.Counter)
        for L, a, n, flag in visits:
            sizes[L][n] += 1
            self.sizes[L][n] += 1
        t0, tsz = z.blocks[1]
        add_at = [a[0] for a in adds]

        def final(i, a):
            """The address an instance visited at index i ends up at (its pool copy if it was in the temp block)."""
            if not (t0 <= a < t0 + tsz):
                return a
            j = bisect.bisect_left(add_at, i + 1)
            while j < len(adds) and not (adds[j][1] <= a < adds[j][1] + adds[j][2]):
                j += 1
            return adds[j][3] + (a - adds[j][1]) if j < len(adds) else None
        starts = collections.defaultdict(set)
        bases = collections.defaultdict(set)
        cur = {}
        for i, (L, a, n, flag) in enumerate(visits):
            fa = final(i, a)
            if fa is None:
                continue
            if n:
                starts[fa].add((L, n))
            bases[L].add(fa)
        pool = {h: t for t, h, p in z.assets}
        # pointer fields from the links: the struct instance containing the field when the child was read
        linked = collections.defaultdict(lambda: collections.defaultdict(list))   # site -> off -> [(base, n, child)]
        for i, j, fa in z.links:
            child, ca, cn, cflag = visits[i]
            site, a, n, flag = visits[j]
            fb = final(j, a)
            if fb is not None:
                linked[site][fa - a].append((fb, cn, child))
        # script-string fields: offset from the instance of the same loader most recently visited
        last = {}
        vi = 0
        for L, field, at in sfields:
            while vi < at:
                Lv, a, n, flag = visits[vi]
                fa = final(vi, a)
                if fa is not None:
                    last[Lv[0]] = (Lv, a, n)
                vi += 1
            if L in last:
                site, a, n = last[L]
                if a <= field < a + max(n, 1):
                    self.sstr[site][field - a] += 1
        for t, h, p in z.assets:
            pass
        for L, c in sizes.items():
            size = site_constant(L)
            if not size:
                continue
            self.instances[L] += len(bases[L])
            for k, obs in linked.get(L, {}).items():
                for fb, n, child in obs:
                    self.fields[L][k][('ptr', (child,))] += 1
                    self.count_obs[(L, k)].append(((self.zone, fb), n))
            for b in bases[L]:
                body = mem.read(b, size)
                for k in range(0, size - 7, 8):
                    if k in linked.get(L, {}):
                        continue
                    v = struct.unpack_from('<Q', body, k)[0]
                    if v == 0:
                        continue
                    if v in pool:
                        self.fields[L][k][('asset', z.types[pool[v]][0])] += 1
                        continue
                    tg = {t for t in starts.get(v, ()) if t[1] and not (t[0] == L and v == b)}
                    if tg:
                        # points at data loaded before, not read here: the game shares identical data
                        self.fields[L][k][('shared', tuple(sorted({t[0] for t in tg}, key=str)))] += 1
                        continue
                    s_ = mem.read(v, 128).split(b'\0')[0]
                    if s_ and len(s_) < 128 and all(32 <= c < 127 for c in s_):
                        self.fields[L][k][('string',)] += 1
                        continue
                    self.fields[L][k][('data',)] += 1
        # count fields are read from the instances' final bytes (kept only for instances with a linked pointer)
        for L, offs in linked.items():
            size = site_constant(L)
            for obs in offs.values():
                for fb, n, child in obs:
                    if (self.zone, fb) not in self.bodies:
                        self.bodies[(self.zone, fb)] = mem.read(fb, size)
        self.zone += 1

    def struct_size(self, L):
        return site_constant(L)

    def element_size(self, L, k):
        """The element size behind pointer field k: the largest struct among its targets, else the common divisor of
        every size the (plain array) target loader read."""
        import math
        best = None
        for key in self.fields[L][k]:
            if key[0] != 'ptr':
                continue
            for c in key[1]:
                cs = self.struct_size(c)
                if cs is not None and cs and (best is None or cs > best):
                    best = cs
            if best is None:
                es = {site_element(c) for c in key[1]} - {None}
                if len(es) == 1:
                    best = es.pop()
                else:
                    g = 0
                    for c in key[1]:
                        for n in self.sizes[c]:
                            g = math.gcd(g, n)
                    best = g or 1
        return best

    def count_field(self, L, k):
        """(offset, width, element size) of the header field equal on every instance to the number of elements the
        pointer at k leads to; (None, None, e) when every instance had exactly one element."""
        obs = self.count_obs.get((L, k))
        if not obs:
            return None
        e = self.element_size(L, k)
        if not e or any(n % e for _, n in obs):
            return None
        if all(n == e for _, n in obs):
            return None, None, e
        if len({n for _, n in obs}) < 2:
            return None       # one count value only: any field holding it would match, so none is claimed
        size = site_constant(L)
        bodies = [(self.bodies[b], n) for b, n in obs]
        for w, fmt in ((4, '<I'), (2, '<H'), (1, '<B')):
            for o in range(0, size - w + 1, w):
                if o <= k < o + 8 or k <= o < k + 8:
                    continue
                if all(struct.unpack_from(fmt, h, o)[0] == n // e for h, n in bodies):
                    return o, w, e
        return None


def type_names():
    rows = {}
    for line in (OUT / 'asset_types.tsv').read_text().splitlines():
        f = line.split('\t')
        if line.startswith('#') or f[0] == 'type' or len(f) < 4 or not f[3]:
            continue
        rows[int(f[3], 16)] = f[1]
    return rows


def site_ids(ev):
    """A stable id per call site: the loader and the site's order among that loader's Load_Stream calls."""
    by = collections.defaultdict(set)
    for site in ev.sizes:
        if site[0] is not None:
            by[site[0]].add(site[1])
    ids = {}
    for L, lines in by.items():
        for i, ln in enumerate(sorted(lines)):
            ids[(L, ln)] = f'{L:X}' + (f'#{i}' if len(lines) > 1 else '')
    return ids


def write(ev):
    ids = site_ids(ev)
    sizes = {}
    for line in (OUT / 'asset_types.tsv').read_text().splitlines():
        f = line.split('\t')
        if not line.startswith('#') and f[0] != 'type' and len(f) > 5 and f[3]:
            sizes[int(f[3], 16)] = (f[1], int(f[5], 16) if f[5] else None)
    # an asset type's header: its struct loader's constant-size site of the header's size
    headers = {}
    for site in ev.sizes:
        if site[0] in sizes and ev.struct_size(site) == sizes[site[0]][1]:
            headers[site] = sizes[site[0]][0]
    # names: header structs by type; others by the first parent field that points at them
    names = {L: n for L, n in headers.items()}
    import math
    for L, c in ev.sizes.items():
        if ev.struct_size(L) is None:      # an array read: named by element size
            g = 0
            for n in c:
                g = math.gcd(g, n)
            g = site_element(L) or g
            names[L] = {1: 'u8[]', 2: 'u16[]', 4: 'u32[]', 8: 'u64[]'}.get(g, f'array(element {g:#x})')
    order = sorted(names, key=lambda L: names[L])
    queue = list(order)
    while queue:
        L = queue.pop(0)
        for k in sorted(ev.fields[L]):
            for key in ev.fields[L][k]:
                if key[0] == 'ptr':
                    for child in key[1]:
                        if child not in names and child != L:
                            names[child] = f'{names[L]}+{k:#x}'
                            queue.append(child)
    rows = ['struct_loader\tname\tsize\tinstances\toffset\tkind\ttarget\tcount_offset\tcount_width\telement_size\tseen']
    by_type = collections.defaultdict(list)
    for L in sorted(ev.sizes, key=lambda x: (x[0] or 0, x[1] or 0)):
        size = ev.struct_size(L)
        if size is None:
            continue
        name = names.get(L, f'struct_{ids.get(L, L)}')
        by_type[name.split('+')[0] if not name.startswith('struct_') else '_unattributed'].append(L)
        kinds = []
        for k in sorted(ev.fields[L]):
            for key, n in ev.fields[L][k].most_common():
                if key[0] == 'data':
                    continue
                target = ''
                if key[0] in ('ptr', 'shared'):
                    target = ' '.join(ids.get(c, '?') + (f'({names[c]})' if c in names else '') for c in key[1])
                elif key[0] == 'asset':
                    target = key[1]
                cf = ev.count_field(L, k) if key[0] == 'ptr' else None
                rows.append('\t'.join([ids.get(L, '?'), name, hex(size), str(ev.instances[L]), hex(k), key[0], target,
                                       hex(cf[0]) if cf and cf[0] is not None else ('one' if cf else ''),
                                       str(cf[1]) if cf and cf[1] else '', hex(cf[2]) if cf else '', str(n)]))
                kinds.append(key[0])
        for o, n in sorted(ev.sstr[L].items()):
            rows.append('\t'.join([ids.get(L, '?'), name, hex(size), str(ev.instances[L]), hex(o), 'scriptstring', '', '',
                                   '', '', str(n)]))
    head = '# GENERATED by tools/assets/layouts.py from the traced zones. Do not edit.\n'
    (OUT / 'layouts.tsv').write_text(head + '\n'.join(rows) + '\n')
    d = OUT / 'layouts'
    import shutil
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir()
    for t, Ls in by_type.items():
        md = [f'# {t}', '', '<!-- GENERATED by tools/assets/layouts.py. Do not edit. -->', '']
        for L in sorted(Ls, key=lambda L: names.get(L, '')):
            size = ev.struct_size(L)
            md += [f'## {names.get(L, f"struct_{ids.get(L)}")} (loader {ids.get(L)}, {size:#x} bytes, '
                   f'{ev.instances[L]} seen)', '',
                   '| Offset | Kind | Target | Count field | Seen |', '|---|---|---|---|---|']
            for line in rows[1:]:
                f = line.split('\t')
                if f[0] != ids.get(L):
                    continue
                cnt = (f'{f[7]} (u{8 * int(f[8])}, element {f[9]})' if f[8] else
                       (f'a single element ({f[9]})' if f[7] == 'one' else ''))
                md.append(f'| {f[4]} | {f[5]} | {f[6]} | {cnt} | {f[10]} |')
            md.append('')
        (d / f'{t}.md').write_text('\n'.join(md))
    return len(rows) - 1, len(by_type)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('zones', nargs='+', help='zone.ff[:zone.fp[:decompressed]]')
    ap.add_argument('--oodle', default=None)
    a = ap.parse_args()
    ev = Evidence()
    oodle = None
    for spec in a.zones:
        parts = spec.split(':')
        ff = Path(parts[0]).read_bytes()
        if len(parts) > 1 and parts[1]:
            import fastfile_patch
            fp = Path(parts[1]).read_bytes()
            header = fastfile_patch.patch_header(fp)[1]
            if len(parts) > 2:
                data = Path(parts[2]).read_bytes()
            else:
                from oodle import Oodle
                oodle = oodle or Oodle(a.oodle)
                data = fastfile_patch.patched(ff, fp, oodle)
        else:
            from oodle import Oodle
            oodle = oodle or Oodle(a.oodle)
            header, data = ff[:zone.HEADER_SIZE], zone.decompress(ff, oodle)
        z, visits, sfields, adds = trace(data, header)
        ev.add_zone(z, visits, sfields, adds)
        print(f'{Path(parts[0]).name}: {len(z.assets)} assets, {len(visits)} struct visits')
    n, t = write(ev)
    print(f'{n} field rows over {sum(1 for L in ev.sizes if ev.struct_size(L))} structs, {t} asset types -> {OUT}')


if __name__ == '__main__':
    main()
