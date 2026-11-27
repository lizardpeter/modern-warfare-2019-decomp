"""The published pseudocode of a build, by address, and the data types Ghidra recorded for globals."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HEAD = re.compile(r'^// ([0-9A-F]{9})  \S+  \(line unknown\)\n(.*?)(?=^// [0-9A-F]{9}  |\Z)', re.S | re.M)
RECORDED = {
    '/undefined8': ('i', 8, False), '/undefined4': ('i', 4, False), '/undefined': ('i', 1, False),
    '/undefined1': ('i', 1, False), '/undefined2': ('i', 2, False), '/uint': ('i', 4, False), '/int': ('i', 4, True),
    '/ushort': ('i', 2, False), '/byte': ('i', 1, False), '/pointer': ('p', ('i', 1, False)),
    '/undefined *': ('p', ('i', 1, False)), '/ulonglong': ('i', 8, False), '/longlong': ('i', 8, True),
    '/float': ('f', 4), '/double': ('f', 8), '/dword': ('i', 4, False), '/qword': ('i', 8, False),
    '/word': ('i', 2, False), '/char': ('i', 1, True),
}


def pseudocode(build='ModernWarfare_TU67'):
    src = {}
    for f in sorted((ROOT / 'analysis' / build / 'pseudocode').rglob('*.c')):
        for m in HEAD.finditer(f.read_text(errors='replace')):
            src[int(m.group(1), 16)] = m.group(2)
    return src


def recorded_types(build='ModernWarfare_TU67'):
    """Ghidra's recorded data type for each .data symbol (ghidra/symbols.tsv), for globals a function's own
    `// global` lines do not cover."""
    out = {}
    for line in (ROOT / 'analysis' / build / 'ghidra' / 'symbols.tsv').read_text().splitlines()[1:]:
        f = line.split('\t')
        if len(f) >= 8 and f[5] == '.data' and f[6] in RECORDED:
            out[int(f[0], 16)] = RECORDED[f[6]]
    return out
