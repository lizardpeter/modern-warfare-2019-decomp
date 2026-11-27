# Animations (xanim, asset type 7)

What TU67 loads for an animation (XAnimParts). Every rule names the function it comes from or says "measured on
<file>"; anything else is marked *unverified*. Field names are ours; where one is a guess from the earlier games'
layout (ghosts-decomp docs/assets/animations.md, IW6 PDB) it says so.

Status: **decoded and checked bit for bit against the game.** `tools/assets/xanim.py` reads an animation and
evaluates it (bones and root motion) exactly as TU67's own evaluators do; `tests/assets/xanim_check.py` calls the
game's functions in the emulator on every animation of a zone at 7 times and compares the result byte for byte
(section 4). Not done: the streamed (`.xpak`) case, additive and blended evaluation (the dispatcher's other modes).

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
| +0x80 | u8 | **flags**: 1 loops (the time wraps, 1440EF0C0), 2 root motion with a 2D (yaw) rotation, 4 with a 3D rotation (1440E9950) |
| +0x81..+0x85 | 5 × u8 | **bones by rotation class** (section 3), summing to the bone count |
| +0x86..+0x89 | 4 × u8 | **bones by translation class**, also summing to the bone count |
| +0x8A | u8 | bone count (the length of the bone-name list) |
| +0x8B | u8 | notify count (1 on every animation measured) |
| +0x8D | u8 | 6 on every animation with data, 2 on `veh8_common_preload` (*unknown*) |

`veh8_common_preload` is the exception: 0 frames, 0 bones, flags 2 (a 2D root motion) and a delta part (+0x58).

The time of an animation is normalised: `t = time / (frames / frame rate)` (1440EF0C0: `+0x7E / +0x6C` is the
length in seconds; with flag 1 the time is wrapped by fmod, otherwise anything past the end is t = 1).

## 3. Bone classes and their data

The format is the earlier games' (ghosts-decomp docs/assets/animations.md 3), with the counts at +0x81..+0x89. The
bone names list the bones in class order; rotation classes take bones in that order, translation classes name
their bone with a byte of the byte data.

| Count | Class | Data (read in this order through the arrays) |
|---|---|---|
| +0x81 | no rotation | identity: adds ±weight to w (negative when the accumulated w is negative) |
| +0x82 | 2D rotation, keyed | (z, w): u16 key count − 1 in the short data, the frame index table, 2 × s16 per key in the random short data |
| +0x83 | rotation, keyed | (x, y, z, w): as above, 4 × s16 per key |
| +0x84 | 2D rotation, one key | (z, w): 2 × s16 in the short data |
| +0x85 | rotation, one key | 4 × s16 in the short data |
| +0x86 | small translation, keyed | bone byte; key count − 1 (short data); frame index table; mins and size (6 × f32 in the int data); 3 × u8 per key in the random byte data |
| +0x87 | translation, keyed | as above, 3 × u16 per key in the random short data (after the rotation keys) |
| +0x88 | translation, one key | bone byte, 3 × f32 in the int data |
| +0x89 | no translation | bone byte (adds weight to the translation weight) |

Rotations are s16 / 32767 (constant 3.051851e-05); a translation is `key × size + mins` per axis and is an offset
added to the bone's base local translation. Frame index tables: under 256 frame intervals, bytes of the byte data
after the key count (translations: after the bone byte); from 256, u16 in the short data when a part has fewer than
0x40 keys, else a coarse table of every 256th entry (`((n − 1) >> 8) + 2` u16 in the short data) with the full table
in the index array (+0x40) — the same as the Store build of Ghosts.

## 4. Evaluation (checked against the game)

The dispatcher 144104C00 picks, for an ordinary animation, 1440FA240 (under 256 frame intervals) or 1440FEC20
(256 or more), or 1440F6600 at t = 1 or with no frames (the last key of every part). Modes 1 and 2 of the
dispatcher are other evaluators (1440F4320 / 1440F7890 / 1440FBA80 and 1440F57D0 / 1440F8F20 / 1440FD4B0; additive
blending, *unverified*). Arguments: (parts, u16 bone map, t, weight, rotTransArray, ignore mask) — the map's high
bit selects mask bit 1 of the eighth word instead of the bone's own bit. Per bone the rotTransArray holds 0x20
bytes: quaternion (4 × f32), translation (3 × f32), translation weight.

For time t, `frame = intervals × t` in float32; a keyed part takes the key i whose table entry holds the frame
(`table[i] <= frame < table[i + 1]`) and interpolates `(k[i+1] − k[i]) × f + k[i]` with
`f = (frame − table[i]) / (table[i+1] − table[i])`. A rotation is then **flipped into the accumulator's hemisphere**
before the weighted add: if `(x·ax + y·ay) + (z·az + w·aw)` (float32, in that order) has its sign bit set, the
rotation is negated — so on a zeroed accumulator, where that sum is +0 or −0 depending on the operands' signs, a
rotation can be stored negated. This differs from Ghosts, which added without flipping. Then
`acc = q × weight + acc` per component; translations `acc = weight × value + acc` and the translation weight
`+= weight`.

Root motion (flags 2 or 4; 1440E9950, arguments (parts, weight, t, out)): the delta part's rotation keys are
interpolated as integers' difference (`(k1 − k0) × f + k0` in float32), then `out = key × weight / 32767 + out`
((z, w) only for 2D; a missing part is the identity (0, 32767)); `out[4] += weight`; the translation as the bones'
(`key × size + mins`), `out[5..7] = weight × value + out`. Layout of the delta part: tools/assets/xanim.py
`read_delta`.

**Checked** (tests/assets/xanim_check.py, every animation at t = 0, 0.1, 0.25, 0.5, 0.731, 0.999 and 1, bit for
bit): `mp_wa_iw8_ar_akilo47_animpackage_tr` (205 animations, 1,435 evaluations) and `mp_wa_iw8_ar_mike4_animpackage_tr`
(167, 1,169) — together every class, 4 animations of 256+ intervals and 2 with split index tables;
`mp_ea_s4_execution_leprechaun_01_tr` and `mp_wa_iw8_fists_mp_ls_package_tr` (301 evaluations and 91 root-motion
evaluations: 2D rotations keyed and single, keyed and single translations). 3D root rotations and small
(byte) root translations did not occur in these zones and are unchecked.

## 5. What Forge needs next

1. Streamed animations: the `.xpak` path (the header's stream fields, if any, are among the bytes not yet named).
2. Additive and blended evaluation (the dispatcher's modes 1 and 2), and the animation trees that use them.
3. Applying an animation to a model: as Ghosts (ghosts-decomp docs/assets/animations.md 5), *unverified* for TU67.
