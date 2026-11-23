# Zones (fastfiles)

How TU67 reads a zone file, from the code that does it. Every rule names the function (TU67 address) it comes from,
or says "measured on <file>"; anything else is *unverified*. Measurements are on the TU63 install's CASC archive
`data.000` (188 zones), whose files are named by archive offset until the TVFS root is read.

Readers: `tools/assets/casc_archive.py` (CASC archive → files), `tools/assets/zone.py` (zone → decompressed zone
data), `tools/assets/oodle.py` (the game's own `oo2core_7_win64.dll` `OodleLZ_Decompress`, run in Unicorn).

## 1. Where zones live

Battle.net CASC. A data archive is a 0x1E0-byte header, then entries: 16-byte encoding key (byte-reversed),
u32 LE entry size, 2 bytes flags, 8 bytes checksums, then a BLTE blob (frames stored `N` or zlib `Z`). Measured:
data.000 has 238 entries, 188 of them zones, plus the TVFS root, the encoding table (`EN`), `IN`, `DL`, Lua
(`--[[`) and localisation files.

## 2. Header (0x88 bytes)

Read by 143755450 (opens the zone, reads 0x88 bytes with 142DED0D0, then checks them).

| Offset | Size | Field | Rule |
|---|---|---|---|
| 0 | 8 | magic | `IWffa100` or `IWffc100`, else DEV ERROR 0x1791 (143754E50); 188/188 measured are `IWffa100` |
| 8 | 4 | version | must be 11 (143754E5A), else DEV ERROR 0x1790 |
| 0xC | 4 | format version | must equal `FORMAT_VERSION[kind]` (143754F20 via 142DEFEC0, table at 147602890), else DEV ERROR 0x1792/0x1793 |
| 0x10 | 2 | *unknown* | 1 in every file measured |
| 0x12 | 1 | kind | index into the format-version table; measured 0, 2, 3, 7, 8 |
| 0x14 | 0xC | *unknown* | |
| 0x20 | 8 | decompressed size | equals the stream's total (measured on every file read) |
| 0x28–0x87 | | *unknown* | sizes per zone memory block, by the look of them (*unverified*) |

The format-version table (identical in TU63 and TU67):

| kind | 0, 1, 6 | 2–5 | 7–16 |
|---|---|---|---|
| version | 0x10C1 | 0xFF3 | 0xFCD |

Measured: kind 2 and 3 zones are 0xFF3 (171), kind 7 and 8 are 0xFCD (13), kind 0 are 0x10C1 (1), 0x10B7 (2),
0x10A3 (1). The 0x10B7/0x10A3 copies would be rejected by both exes: they are most likely unreferenced data left
in the archive by older patches (confirm against the TVFS root). Both 0x10B7 files also stop decoding partway (block
685 of one), as overwritten leftovers would.

## 3. Signed block (0x8004 bytes)

At 0x88: `IWffs100`, 4 zero bytes, then high-entropy data to 0x808C (measured, every file). Checked by 142DED590
(compares `IWffs100`); the rest is *unverified* (by its size, a signature and hash table).

## 4. Stream (from 0x808C)

Read by 142DEF240 (state struct fields +0x8E8B8 onward).

- 8-byte stream header: u32 total decompressed size; bytes 4–6 (`00 00 01` measured); byte 7 the codec
  (142DEF29F): 1 stored (memcpy, 142DEF0C0), 4 and 5 through 147248D50 (*unidentified*), 6 and 7 Oodle
  (142DEF0E0), anything else DEV ERROR 0x298. Every zone measured is codec 6.
- Then blocks until the total is reached, each: u32 compressed size, u32 decompressed size, u32 check value
  (0 in every block measured; when the stream has a verify context at +0x8E920 the block is checked by
  142F19A10/142F19530, *unverified* what they compute), then the data, padded to a multiple of 4 (142DEF335).
- Oodle call (142DEF43B): `OodleLZ_Decompress(src, compSize, dst, decompSize, fuzzSafe=1, checkCRC=0,
  verbosity=0, 0, 0, 0, 0, decoderMemory, 0x6C0B8, threadPhase=3)`; anything but a non-zero result fails the
  load. Blocks decompress to 0x10000 bytes (measured), the last to the remainder.

Measured: 186 of the 188 zones in data.000 decompress to exactly header +0x20 bytes (every zone at its table's format
version, and the 0x10A3 copy too); the two that fail are the 0x10B7 copies. The first zone of
data.000 leaves 0x2BD0 bytes after its last block (*unidentified*).

## 5. Zone data: the asset list

Measured on the 185 zones of data.000 at their current format version (`zone.asset_list`); the loader that reads it
is still to be traced in the code.

| Offset | Size | Field |
|---|---|---|
| 0x0 | 4 (+4 pad) | script-string count |
| 0x8 | 8 | script-string array pointer (-2: follows) |
| 0x10 | 4 (+4 pad) | asset count |
| 0x18 | 8 | asset array pointer (-2: follows) |
| 0x20 | 8 × count | string pointers; each -2 has its string follow, NUL-terminated, after the array |
| … | 16 × count | assets: u32 XAssetType, pad, header pointer (-2: the header follows) |

Pointers of -2 mean "the data follows inline in the stream", as in the earlier IW games. Every asset type in all 185
lists is in range (0–121), which confirms the enum order of the name table (docs/assets.md). The first zone of
data.000 has 745 strings (prop model names such as `ac_unit_large`) and 2 assets, an edgelist (116) and a
collisiontile (107); the kind-0 zone has 4,383 assets.

Asset types in data.000's zones: material 2,926, techset 856, xmodeldetailcollision 422, xmodelsurfs 392,
pixelshader 339, physicsasset 315, vertexshader 196, gfx_map_trzone 140, fx_map_trzone 140, streaminginfo 120,
image 32, edgelist 31, collisiontile 31, domainshader 28, xmodel 19, decalvolumematerial 19, hullshader 17,
dynentitylist 6, rawfile 1, keyvaluepairs 1.

Next: the asset headers themselves. Each type's header follows its asset entry's stream position in load order;
reading them needs each type's layout and the zone's memory blocks and pointer fix-ups, from the loader after
142DEF240.
