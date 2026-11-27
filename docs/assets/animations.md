# Animations (xanim, asset type 7)

What TU67 loads for an animation (XAnimParts). Every rule names the function it comes from or says "measured on
<file>"; anything else is marked *unverified*. Field names are ours; where one is a guess from the earlier games'
layout (ghosts-decomp docs/assets/animations.md, IW6 PDB) it says so.

Status: the **header and everything it points to are located** (the loader below). The meaning of the compressed
track data (how bone rotations and translations are decoded per frame) needs the animation evaluation code and is
not done yet; nor is the streamed (`.xpak`) case.

## 1. How it is loaded

`Load_XAnimPartsPtr` 142E544F0 (asset header pointer rules: docs/assets/zones.md 8), then `Load_XAnimParts`
142E53F80, then the wrapper 14311AE60 (`DB_AddXAsset(7, …)`). The header is 0xA8 bytes; everything it points to is
read in block 5, in this order:

| Off | Field | How it is read (142E53F80) |
|---|---|---|
| +0x00 | name | XString (142E45CC0) |
| +0x08 | bone names | −1/−2/offset; 4-aligned array of **script strings**, count = u8 +0x8A (142E46280) |
| +0x48 | notifies | any non-zero: 4-aligned, u8 +0x8B entries of 8 bytes (142E53DD0); each entry's first 4 bytes are a script string (142E46250); the other 4 are *unverified* (a time, by the earlier games) |
| +0x50 | second notify list | as +0x48, count u8 +0x8C |
| +0x58 | delta part | any non-zero: 8-aligned 0x18 bytes (142E53740): three pointers, each non-zero one 8-aligned and loaded by 142E53E70, 142E53840 and 142E538E0 (*not yet read*) |
| +0x10 | byte data | −1/−2/offset; bytes, count u32 +0x74 |
| +0x18 | short data | −1/−2/offset; 2-aligned u16, count u16 +0x78 |
| +0x20 | int data | −1/−2/offset; 4-aligned u32, count u16 +0x7A |
| +0x28 | random short data | −1/−2/offset; 2-aligned u16, count u32 +0x60 |
| +0x30 | random byte data | −1/−2/offset; bytes, count u32 +0x64 |
| +0x38 | random int data | −1/−2/offset; 4-aligned u32, count u16 +0x7C |
| +0x40 | frame indices | any non-zero: count u32 +0x68; **bytes when the frame count (u16 +0x7E) is below 0x100, else 2-aligned u16** |
| +0x98 | a second script-string list | any non-zero: 4-aligned, count u16 +0x90 |
| +0xA0 | u16 table | any non-zero: 2-aligned u16, count `(frames + 1) × u16 +0x90` |

The data names (byte/short/int, "random") follow the earlier games, whose XAnimParts had the same six arrays; that
they mean the same here is *unverified* until the evaluation code is read.

## 2. Other header fields (measured)

Measured on the 25 animations of the patched `mp_t_gun_course` after the game's own load (tests/assets/zone_emu.py):

| Off | Size | Value |
|---|---|---|
| +0x6C | f32 | 30.0 in every one: frame rate (*unverified* name) |
| +0x70 | f32 | `frame rate / (frames − 1)`: 0.789 for 38 frames (`veh8_common_hatchback_explode`), 1.0714 for 29, 1.7647 for 18 — the reciprocal of the duration in seconds |
| +0x7E | u16 | frame count (also decides the index width above) |
| +0x80..+0x83 | 4 × u8 | bones by rotation class: on every animation with bones they **sum to the bone count +0x8A** (e.g. `pickup_expl_rock`: 0, 12, 0, 1 for 13 bones; `hatchback_explode`: 0, 0, 0, 5). The earlier games kept `boneCount[]` by compression kind in this order (no / half / full rotation, …); which class is which here is *unverified* |
| +0x84, +0x85 | 2 × u8 | 0 on every animation measured |
| +0x86..+0x89 | 4 × u8 | bones by translation class: they **also sum to +0x8A** (`pickup_expl_lb_2`: 3, 3, 0, 7 for 13); +0x89 is the largest for most and is probably "no translation" (*unverified*) |
| +0x8A | u8 | bone count (the length of the bone-name list) |
| +0x8B | u8 | notify count (1 on every animation measured) |
| +0x8D | u8 | 6 on every animation with data, 2 on `veh8_common_preload` (*unknown*) |

`veh8_common_preload` is the exception throughout: 0 frames, 0 bones, +0x80 = 2, and the only one with a delta part
(+0x58).

## 3. What Forge needs next

1. The track decoder: find the TU67 functions that evaluate an XAnimParts (they read the six arrays and the index
   table), document the encoding per bone-count class, and check a decoded pose against the game.
2. Streamed animations: the `.xpak` path (the header's stream fields, if any, are among the bytes not yet named).
3. A Python reader (`tools/assets/xanim.py`) checked against the emulator's loaded copy byte for byte.
