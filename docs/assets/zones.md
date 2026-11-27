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

Measured (zones of data.000 and data.006, named through the TVFS): every kind 2, 3, 7, 8 and 12 zone is at its
table's version. Kind 0 zones are often at an older version (`englisheng_common` 0x10A3, `srv_cp_arms_dealer` 0x10B7,
`mp_downtown_gw` 0x10B7, `common_mp` 0xFCF, `mp_t_gun_course` 0x100C): these are **base files that a fastfile patch
(`.fp`, section 7) brings to the current version**. The check runs on the patched header, so they load. (An earlier
version of this document called them stale leftovers; that was wrong.)

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

Measured: 186 of the 188 zones in data.000 decompress to exactly header +0x20 bytes. The two that do not,
`mp_downtown_gw` and `proxywar`, have data-carrying patches (section 7): their base stream on its own is not the
zone the game loads. The first zone of
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

## 6. Asset headers

For each entry of the asset list, `Load_XAssetHeader` (142E2ECF0) dispatches on the type: a chain of
`if (type == N) { Load_<T>Ptr(); … }`, one case for each of 114 types (iesprofile, ui_map, aitype, mptype,
character, xmodelalias, string and assetlist have none). Every case was extracted by `tools/assets/asset_types.py`
into analysis/ModernWarfare_TU67/assets/asset_types.tsv (loader addresses, stream block, header size).

`Load_<T>Ptr` (e.g. 142E7BF90 for physicslibrary):

1. reads the 8-byte header pointer (143760AE0, `DB_LoadXFileData(atStreamStart, ptr, size)`);
2. by its value: 0 = no asset; -1 = allocate and read the header inline (142DF2230 first); -2 = the header follows
   inline; -3 = the header follows inline and the pointer's own location is saved (1437604F0); any other value is a
   reference to data already loaded, resolved by 142DFEF30;
3. for inline headers, pushes a stream block (142DF1380: block 7 for 108 types; 15 for image, gfx_map, vfx and
   vectorfield; 31 for particlesimanimation), calls the struct loader `Load_<T>(0)`, and registers the asset:
   143757490 (`DB_AddXAsset(type, &header)`) for most types, a type-specific function for others (xanim 14311AE60,
   gfx_map 14311AB40).

The struct loader reads the fixed-size header (its size is the R8D argument of 143760AE0), then each pointer field's
data in turn, the same markers applying.

**Checked on data**: the first zone's first asset is an edgelist (header 0xA0). Its 0xA0 bytes after the asset list
hold the -2 name marker at +0, float bounds, and counts paired with -2 pointers; the edgelist's name
(`mapedgelist_0042…`) begins exactly at +0xA0.

Selected header sizes (the full table is the generated TSV): weapon 0x290, attachment 0x458, camo 0x128, xanim
0xA8, xmodel 0x2B0, xmodelsurfs 0x60, material 0x78, techset 0x40, image 0xE8, soundbank 0x200, vfx 0x40,
vehicle 0x1030, gfx_map 0x4610, playeranim 0xA8, suit 0x720, reticle 0x48.

Next: each header's fields and their pointed-to data, type by type, starting with what Forge needs (weapon,
attachment, xmodel, xanim, material, image, soundbank).

## 7. Fastfile patches (`.fp`)

Every one of the install's 2,934 `.fp` files pairs with a `.ff` of the same name: 1,162 change only the header
(328 bytes), 1,772 carry data (`common_mp.fp` 178 MB). Read by 143755450 together with the base zone.

| Offset | Size | Field |
|---|---|---|
| 0 | 8 | `IWffd100` |
| 8 | 4 | 6 |
| 0xC | 4 | must be 4, else DEV ERROR 0x1798 (143755450) |
| 0x10–0x37 | | sizes, *partly identified*: `mp_t_gun_course.fp` has +0x10 0x200000, +0x18 0x7FC45EF, +0x20 0x1FC71C, +0x28 0x6C8000 (the patch body size), +0x30 0x84E185 (the decompressed delta size) |
| 0x38 | 0x88 | the base zone's header, which must match the `.ff` byte for byte (memcmp, else DEV ERROR 0x1799) |
| 0xC0 | 0x88 | the patched header: replaces the base header, and is what the format-version check (143754F20) sees |
| 0x148 | | for data patches: an `IWffs100` signed block (0x8004 bytes) and a compressed block stream, as in a zone (section 4) |

Measured: `srv_cp_arms_dealer.fp` (header only) changes only +0xC (0x10B7 → 0x10C1). `mp_t_gun_course.fp` changes
version, decompressed size (0x136EA2B2 → 0x11AC2F37) and most block sizes; its stream (133 blocks) decompresses to
exactly +0x30 bytes, leaving 0x39A8 bytes after the last block.

**The decompressed patch is VCDIFF** (RFC 3284 magic `D6 C3 C4 00`), applied to the decompressed base zone. Its header
indicator is 0x0C, which standard VCDIFF does not define (0x04 is xdelta3's application header; 0x08 is unknown), so
it is a variant: the decoder in the exe is to be found and followed before a reader is written. The game ships no
default code table as data (searched), so it is likely built at run time, as xdelta3 does.
