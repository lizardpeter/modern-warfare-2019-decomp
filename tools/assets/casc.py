#!/usr/bin/env python3
"""Read a Battle.net CASC install by file name: build config -> local indices -> encoding -> TVFS. Standard library
only (plus casc_archive.py). See docs/assets/casc.md.

    python3 tools/assets/casc.py <install root> ls [glob]          # every file: path, size, archive, present?
    python3 tools/assets/casc.py <install root> get <path> <out>   # extract one file

<install root> is a folder holding `.build.info` and `Data/` (config, data/*.idx, data/data.NNN). Archives that are
missing (e.g. still uploading) are reported, not fatal.
"""
import fnmatch
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from casc_archive import ENTRY_HEADER, blte_frames  # noqa: E402


class Casc:
    def __init__(self, root):
        self.root = Path(root)
        info = (self.root / ".build.info").read_text().splitlines()
        cols = [c.split("!")[0] for c in info[0].split("|")]
        row = dict(zip(cols, info[1].split("|")))
        self.version = row["Version"]
        bk = row["Build Key"]
        self.config = {}
        for line in (self.root / "Data/config" / bk[:2] / bk[2:4] / bk).read_text().splitlines():
            if " = " in line:
                k, v = line.split(" = ", 1)
                self.config[k] = v.split()
        self.index = self._read_indices()
        self._ckey_to_ekey = None

    # --- local indices: 9-byte EKey prefix -> (archive, offset, size) ---
    def _read_indices(self):
        latest = {}
        for f in sorted((self.root / "Data/data").glob("*.idx")):
            bucket, ver = int(f.stem[:2], 16), int(f.stem[2:], 16)
            if latest.get(bucket, (-1,))[0] < ver:
                latest[bucket] = (ver, f)
        index = {}
        for _, f in latest.values():
            d = f.read_bytes()
            hs = struct.unpack_from("<I", d, 0)[0]
            p = (8 + hs + 15) & ~15
            size = struct.unpack_from("<I", d, p)[0]
            p += 8
            for q in range(p, p + size - size % 18, 18):
                key = d[q:q + 9]
                hi, lo = d[q + 9], struct.unpack_from(">I", d, q + 10)[0]
                archive = (hi << 2) | (lo >> 30)
                index[key] = (archive, lo & 0x3FFFFFFF, struct.unpack_from("<I", d, q + 14)[0])
        return index

    def archive_path(self, n):
        return self.root / "Data/data" / f"data.{n:03d}"

    def locate(self, ekey: bytes):
        return self.index.get(ekey[:9])

    def read_ekey(self, ekey: bytes) -> bytes:
        loc = self.locate(ekey)
        if loc is None:
            raise KeyError(f"{ekey.hex()}: not in the local indices")
        archive, off, size = loc
        path = self.archive_path(archive)
        if not path.exists():
            raise FileNotFoundError(f"{ekey.hex()}: in {path.name}, which is not present")
        with open(path, "rb") as f:
            f.seek(off)
            blob = f.read(size)
        if blob[:16][::-1][:9] != ekey[:9] or blob[ENTRY_HEADER:ENTRY_HEADER + 4] != b"BLTE":
            raise ValueError(f"{ekey.hex()}: archive entry at {path.name}:{off:#x} does not match")
        parts = list(blte_frames(blob[ENTRY_HEADER:]))
        if any(p is None for p in parts):
            raise ValueError(f"{ekey.hex()}: frame mode not supported")
        return b"".join(parts)

    # --- TVFS: path -> list of EKey spans ---
    def files(self):
        """Yield (path, [(ekey, content offset, size)]) for every file in the vfs-root TVFS."""
        yield from self._tvfs(bytes.fromhex(self.config["vfs-root"][1]), "")

    def _tvfs(self, ekey, prefix):
        d = self.read_ekey(ekey)
        if d[:4] != b"TVFS":
            raise ValueError("not TVFS")
        ver, hsize, ek_size, pk_size, flags = d[4], d[5], d[6], d[7], struct.unpack_from(">I", d, 8)[0]
        pt_off, pt_size, vfs_off, vfs_size, cft_off, cft_size = struct.unpack_from(">6I", d, 12)
        cft_ofs_size = 4 if cft_size > 0xFFFFFF else 3 if cft_size > 0xFFFF else 2 if cft_size > 0xFF else 1
        span_rec = 4 + 4 + cft_ofs_size

        def spans(vfs_pos):
            n = d[vfs_off + vfs_pos]
            out = []
            q = vfs_off + vfs_pos + 1
            for _ in range(n):
                coff, csize = struct.unpack_from(">II", d, q)
                cft = int.from_bytes(d[q + 8:q + 8 + cft_ofs_size], "big")
                ek = d[cft_off + cft:cft_off + cft + ek_size]
                out.append((ek, coff, csize))
                q += span_rec
            return out

        # Path table: a radix tree (measured on this build). An entry is [0x00 = separator] [len, name fragment]
        # [0x00 = separator], then optionally 0xFF + u32 BE node value. The fragment is appended to the current
        # prefix. Value with the top bit set: a folder whose children follow and span (value & 0x7FFFFFFF) - 4
        # bytes; otherwise a file, the value being its offset in the VFS (span) table. A fragment with no node value
        # keeps extending the prefix for the following entry. After a node the prefix resets to the parent's.
        out = []

        def walk(pos, end, parent):
            cur = parent
            while pos < end:
                if d[pos] == 0:
                    cur += b"/"
                    pos += 1
                if pos < end and d[pos] != 0xFF:
                    n = d[pos]
                    cur += d[pos + 1:pos + 1 + n]
                    pos += 1 + n
                    if pos < end and d[pos] == 0:
                        cur += b"/"
                        pos += 1
                if pos < end and d[pos] == 0xFF:
                    val = struct.unpack_from(">I", d, pos + 1)[0]
                    pos += 5
                    if val & 0x80000000:
                        sub = (val & 0x7FFFFFFF) - 4
                        walk(pos, pos + sub, cur)
                        pos += sub
                    else:
                        out.append((cur, val))
                    cur = parent

        walk(pt_off, pt_off + pt_size, prefix.encode())
        for path, vfs_pos in out:
            yield path.decode("utf-8", "replace"), spans(vfs_pos)

    def read(self, spans_):
        return b"".join(self.read_ekey(ek)[:sz] for ek, _, sz in spans_)


def main():
    c = Casc(sys.argv[1])
    cmd = sys.argv[2]
    if cmd == "ls":
        pat = sys.argv[3] if len(sys.argv) > 3 else "*"
        for path, sp in c.files():
            if fnmatch.fnmatch(path, pat):
                locs = [c.locate(ek) for ek, _, _ in sp]
                here = all(l and c.archive_path(l[0]).exists() for l in locs)
                arch = ",".join(f"{l[0]:03d}" if l else "?" for l in locs)
                print(f"{path}\t{sum(s for _, _, s in sp)}\t{arch}\t{'yes' if here else 'no'}")
    elif cmd == "get":
        for path, sp in c.files():
            if path == sys.argv[3]:
                Path(sys.argv[4]).write_bytes(c.read(sp))
                return
        raise SystemExit("no such file")


if __name__ == "__main__":
    main()
