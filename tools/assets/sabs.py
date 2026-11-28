#!/usr/bin/env python3
"""Read sound banks (`.sabs`): their entries and Opus audio. Format: docs/assets/sound.md.

    python3 tools/assets/sabs.py <bank.sabs> [--wav out_dir]     list entries, optionally write WAV files

`Bank(source)` takes a path or an object with `read(offset, size)`. Decoding needs libopus (ctypes).
"""
from __future__ import annotations

import argparse
import ctypes
import ctypes.util
import struct
import wave
from dataclasses import dataclass
from pathlib import Path

MAGIC = 0x23585532
OPUS = 14


@dataclass
class Sound:
    id: int
    size: int            # bytes of packets
    table_size: int      # bytes of the packet offset table before them
    samples: int         # playable samples per channel
    offset: int          # file offset of the table
    rate: int
    codec: int
    flags: bytes         # +0x20..+0x2B, *partly unknown*


class _File:
    def __init__(self, path):
        self.f = open(path, "rb")

    def read(self, off, n):
        self.f.seek(off)
        return self.f.read(n)


class Bank:
    def __init__(self, source):
        self.src = _File(source) if isinstance(source, (str, Path)) else source
        h = self.src.read(0, 0x48)
        magic, version, esize, _, _, count = struct.unpack_from("<6I", h, 0)
        if magic != MAGIC:
            raise ValueError(f"not a sound bank (magic {magic:#x})")
        self.version, self.entry_size, self.count = version, esize, count
        self.file_size, self.entries_offset, self.second_offset = struct.unpack_from("<3Q", h, 0x20)

    def sounds(self):
        raw = self.src.read(self.entries_offset, self.entry_size * self.count)
        out = []
        for i in range(self.count):
            e = raw[i * self.entry_size:(i + 1) * self.entry_size]
            sid, size, table, samples, _, offset, _, rate = struct.unpack_from("<8I", e, 0)
            out.append(Sound(sid, size, table, samples, offset, rate, e[0x22], e[0x20:0x2C]))
        return out

    def packets(self, s: Sound):
        """Opus packets: a table of u32 offsets (one per 960-sample packet, relative to the first packet), then
        packets stored as {u16 length, bytes}."""
        n = s.table_size // 4
        table = list(struct.unpack(f"<{n}I", self.src.read(s.offset, s.table_size))) + [s.size]
        blob = self.src.read(s.offset + s.table_size, s.size)
        for k in range(n):
            p = blob[table[k]:table[k + 1]]
            length = struct.unpack_from("<H", p, 0)[0]
            yield p[2:2 + length]

    def decode(self, s: Sound):
        """(channels, interleaved int16 PCM bytes, trimmed to the stored sample count)."""
        if s.codec != OPUS:
            raise ValueError(f"codec {s.codec} not handled")
        packets = list(self.packets(s))
        channels = s.flags[0]          # +0x20; equals the Opus TOC stereo bit on all 705 sounds measured
        lib = ctypes.CDLL(ctypes.util.find_library("opus") or "libopus.so.0")
        lib.opus_decoder_create.restype = ctypes.c_void_p
        lib.opus_decode.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int32,
                                    ctypes.POINTER(ctypes.c_int16), ctypes.c_int, ctypes.c_int]
        err = ctypes.c_int()
        dec = lib.opus_decoder_create(s.rate, channels, ctypes.byref(err))
        buf = (ctypes.c_int16 * (5760 * channels))()
        pcm = bytearray()
        for p in packets:
            n = lib.opus_decode(dec, p, len(p), buf, 5760, 0)
            if n < 0:
                raise ValueError(f"opus error {n}")
            pcm += bytes(buf)[:n * channels * 2]
        lib.opus_decoder_destroy.argtypes = [ctypes.c_void_p]
        lib.opus_decoder_destroy(dec)
        return channels, bytes(pcm[:s.samples * channels * 2])


@dataclass
class AliasEntry:
    file: str            # e.g. "ambient\\amb_mp_quarry_interior_lr.SL.75.36000.all"
    sound_id: int        # the .sabs entry id
    params: bytes        # 0xB0 bytes (volumes, distances, …; *fields not named*)
    names: tuple         # the 0x28-byte record at +0x10: four name strings (142E69120)


def read_aliases(read, header: int):
    """Sound aliases of a soundbank asset (0x200 bytes, loader 142EB6360): +0x20 u64 count and +0x28 array of
    0x20-byte alias lists {name, u32 hash (+0x08), entries (+0x10), u32 entry count (+0x18)} (142E68EC0); each
    entry 0x20 bytes {file name, u32 sound id (+0x08), u32 (+0x0C), record (+0x10), params (+0x18)}
    (142E68C50). Returns {alias name: [AliasEntry]}."""
    q = lambda a: struct.unpack("<Q", read(a, 8))[0]

    def cstr(p):
        if not p:
            return None
        out = bytearray()
        while True:
            chunk = read(p + len(out), 64)
            i = chunk.find(b"\0")
            if i >= 0:
                out += chunk[:i]
                return out.decode("latin1")
            out += chunk

    out = {}
    count, lists = q(header + 0x20), q(header + 0x28)
    for i in range(count):
        lst = read(lists + 0x20 * i, 0x20)
        name = cstr(struct.unpack_from("<Q", lst, 0)[0])
        entries, n = struct.unpack_from("<Q", lst, 0x10)[0], struct.unpack_from("<i", lst, 0x18)[0]
        items = []
        for k in range(n):
            e = read(entries + 0x20 * k, 0x20)
            rec, par = struct.unpack_from("<QQ", e, 0x10)
            names = tuple(cstr(struct.unpack_from("<Q", read(rec, 0x28), o)[0]) for o in (0, 8, 0x18, 0x20)) if rec else ()
            items.append(AliasEntry(cstr(struct.unpack_from("<Q", e, 0)[0]), struct.unpack_from("<I", e, 8)[0],
                                    read(par, 0xB0) if par else b"", names))
        out[name] = items
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bank")
    ap.add_argument("--wav", type=Path)
    a = ap.parse_args()
    b = Bank(a.bank)
    for s in b.sounds():
        print(f"{s.id:08x}: {s.samples / s.rate:.2f} s at {s.rate} Hz, codec {s.codec}, {s.size} bytes")
        if a.wav:
            a.wav.mkdir(parents=True, exist_ok=True)
            ch, pcm = b.decode(s)
            with wave.open(str(a.wav / f"{s.id:08x}.wav"), "wb") as w:
                w.setnchannels(ch)
                w.setsampwidth(2)
                w.setframerate(s.rate)
                w.writeframes(pcm)


if __name__ == "__main__":
    main()
