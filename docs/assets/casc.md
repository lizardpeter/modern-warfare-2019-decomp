# CASC (the Battle.net install)

`tools/assets/casc.py` reads the install by file name. Measured on the TU63 install (1.63.3.12428344).

1. `.build.info`: pipe-separated, first row column names; `Build Key` names the build config at
   `Data/config/<k[0:2]>/<k[2:4]>/<k>` (`key = value` lines). This build's `build-name` is
   `live_12428344_TU_WZ_351_8_24_C_r_signed_ship`.
2. Local indices `Data/data/<bucket><version>.idx` (16 buckets; the highest version of each wins): 8-byte header
   prefix (u32 header size 0x10, u32 hash), the header (version 7, key size 9, offset size 5, size field 4, 30
   segment bits), aligned to 16, then u32 entries size, u32 hash, then 18-byte entries: 9-byte encoding-key prefix,
   1 + 4 bytes big-endian offset (archive number = high bits, 30-bit offset), u32 LE size. 61,837 entries.
3. Archive entries (docs/assets/zones.md 1): the entry header repeats the encoding key (byte-reversed); the reader
   checks it.
4. `vfs-root` (the build config's second key is the encoding key): a TVFS file (`TVFS`, version 1, header 0x2E,
   encoding-key size 9, flags 0xF). Path table, VFS table and container-file table offsets and sizes follow as BE u32.
   The path table is a radix tree: an entry is [0x00 separator] [u8 length, name fragment] [0x00 separator], then
   0xFF + u32 BE node value; the fragment extends the parent's prefix. Top bit set: a folder whose children span
   (value & 0x7FFFFFFF) - 4 bytes; otherwise a file, the value being its offset in the VFS table. A VFS entry is a
   span count, then per span: u32 BE content offset, u32 BE size, a 3-byte BE offset into the container-file table
   (that table's size needs 3 bytes), where the encoding key is.
   72,833 files. The encoding table is not needed for TVFS files (they name encoding keys directly).

Files in archives not yet uploaded are listed with `present = no`.
