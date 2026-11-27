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
