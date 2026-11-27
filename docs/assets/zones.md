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

## 3. Signed unit and hash chain

After the header the file is read in **0x4000-byte units** (142DED8E0), each passed to 142DED590, which keeps a
two-level SHA-256 chain. `tools/assets/zone.stream()` follows it and verifies every hash. Measured on
`mp_t_gun_course` (326 MB), `proxywar` and `mp_downtown_gw` (all three hashes levels match on every unit).

| Unit | Content | Check (142DED590) |
|---|---|---|
| 0 | the signed unit: `IWffs100`, 4 bytes 0, at +0xC SHA-256 of bytes 0x12C..0x1970, at +0x2C a 0x100-byte signature, at +0x12C the zone name (0x40 bytes, NUL-padded; e.g. `mp_t_gun_course`), at +0x16C 4 bytes, at +0x170 **192 SHA-256 hashes**, one per hash table; the rest of the unit unused | magic; SHA-256 at +0xC; signature by 142DED760 (*not checked by the reader*: needs the game's key); name compared with the zone requested |
| 1 | hash table 0: **512 SHA-256 hashes**, one per following data unit | its SHA-256 equals the signed unit's entry 0 |
| 2–513 | 512 data units (8 MB) | each SHA-256 equals its table entry |
| 514 | hash table 1 | equals the signed unit's entry 1 |
| … | and so on; the last data unit may be short | |

The function's own hash is 143754AE0 (SHA-256, confirmed by matching values). The data units joined together are
the zone's data. (An earlier version of this document took the signed unit for a 0x8004-byte block and missed the
hash tables, so zones over 8 MB failed to decode partway: `mp_downtown_gw`, `proxywar`, `mp_t_gun_course`. With the
tables skipped they decode completely.)

## 4. Stream (the data, from file offset 0x8088 when the zone has no more than 8 MB)

Read by 142DEF240 (state struct fields +0x8E8B8 onward). The data starts with 4 bytes `02 49 57 43` ("\x02IWC",
every zone read), then:

- 8-byte stream header: u32 total decompressed size; bytes 4–6 (`00 00 01` measured); byte 7 the codec
  (142DEF29F): 1 stored (memcpy, 142DEF0C0), 4 and 5 through 147248D50 (*unidentified*), 6 and 7 Oodle
  (142DEF0E0), anything else DEV ERROR 0x298. Every zone measured is codec 6.
- Then blocks until the total is reached, each: u32 compressed size, u32 decompressed size, u32 check value
  (0 in every block measured; when the stream has a verify context at +0x8E920 the block is checked by
  142F19A10/142F19530, *unverified* what they compute), then the data, padded to a multiple of 4 (142DEF335).
- Oodle call (142DEF43B): `OodleLZ_Decompress(src, compSize, dst, decompSize, fuzzSafe=1, checkCRC=0,
  verbosity=0, 0, 0, 0, 0, decoderMemory, 0x6C0B8, threadPhase=3)`; anything but a non-zero result fails the
  load. Blocks decompress to 0x10000 bytes (measured), the last to the remainder.

Measured: all 188 zones in data.000 and `mp_t_gun_course` decompress to exactly header +0x20 bytes, with every
SHA-256 in the chain matching. The first zone of
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
(328 bytes), 1,772 carry data (`common_mp.fp` 178 MB). Read by 143755450 together with the base zone; 143755060
gives each patch a reader whose source is the base (patch handle +0x190) or the previous patch (+0x188), at most two
patches (142DEE970).

| Offset | Size | Field |
|---|---|---|
| 0 | 8 | `IWffd100` |
| 8 | 4 | 6 |
| 0xC | 4 | must be 4, else DEV ERROR 0x1798 (143755450) |
| 0x10 | 8 | target window size: 0x200000 (`mp_t_gun_course`) |
| 0x18 | 8 | *unidentified* (0x7FC45EF) |
| 0x20 | 8 | *unidentified* (0x1FC71C) |
| 0x28 | 8 | patch body size in the file (0x6C8000) |
| 0x30 | 8 | decompressed delta size (0x84E185) |
| 0x38 | 0x88 | the base zone's header, which must match the `.ff` byte for byte (memcmp, else DEV ERROR 0x1799) |
| 0xC0 | 0x88 | the patched header: replaces the base header, and is what the format-version check (143754F20) sees |
| 0x148 | | data patches only: the same unit layout as a zone (section 3: signed unit, hash tables, data units) holding the same block stream (section 4: `\x02IWC`, stream header, Oodle blocks) |

Measured: `srv_cp_arms_dealer.fp` (header only) changes only +0xC (0x10B7 → 0x10C1). `mp_t_gun_course.fp` changes
version (0x100C → 0x10C1), decompressed size (0x136EA2B2 → 0x11AC2F37) and most block sizes; its stream decompresses
to exactly +0x30 bytes.

### The delta: VCDIFF with two extensions

The decompressed patch is VCDIFF (RFC 3284) that turns the **decompressed base zone into the decompressed patched
zone**. Measured on `mp_t_gun_course.fp` by decoding it; the decoder in the exe is not found yet (it is not in the
zone stream module 142DE*/142DF*, and the exe has no default code table as data, so it is built at run time).

- Header: `D6 C3 C4 00`, header indicator 0x0C (no code table, no secondary compressor, no application header data
  follows; bits 0x04 and 0x08 are outside the RFC and their header-level meaning is *unknown*), then windows.
- Window: indicator byte. 0x01 VCD_SOURCE as in the RFC (source segment length, then position, as varints, into the
  base zone). **0x04: one more varint after the source fields** (*meaning unknown*; 0x28D4 in window 1, 0x2C1D in the
  copy-only windows). **0x08: a 4-byte trailer after the window** (*unidentified*: not adler32, crc32, xxh32 or xxh64
  of the window's output, its encoding or the source slice). Then the RFC window: delta length, target length,
  delta indicator, the three section lengths, the sections, with the RFC default code table and address caches.
- `mp_t_gun_course.fp`: 142 windows, back to back, ending exactly at the end of the delta; their target lengths sum
  to 0x11AC2F37, the patched size; 2 MB each except the last. Window 0 decoded with the default code table gives
  `E8 04 00 00 … FE FF …`: a zone asset list (0x4E8 strings, 0x24BA assets), against the base's 0x4DD strings and
  0x1640 assets. Windows 4–11 are 14-byte copies of 2 MB from the base.
- Source segments are large (window 0: 0x76EC9DC bytes from 0x2716; window 1: 0x76EC684 from 0x2A6E; both end at
  0x76EF0F2).

Next: find the decoder (it reads the bytes in this layout, so the 0x04 and 0x08 fields will show their meaning),
then `tools/assets/fastfile_patch.py` applies a patch and `zone.py` reads the patched zone.
