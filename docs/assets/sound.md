# Sound (`.sabs` banks)

Audio is in `.sabs` files (5,629 in the install; 1,074 in the uploaded archives), per map, mode and language
(`mp_t_gun_course.sabs`, `englisheng_mp_t_gun_course.sabs`, `patch_…`). Measured on `mp_t_gun_course.sabs`
(15,155,328 bytes, 705 sounds); read by `tools/assets/sabs.py`. Status: **all 705 sounds decode**, and the zone's
`soundbank` aliases are linked to them by id; the alias parameters (volume, distances, …) are located but not
named.

## Header

| Off | Field | Measured |
|---|---|---|
| +0x00 | u32 magic 0x23585532 | |
| +0x04 | u32 version 10 | |
| +0x08 | u32 entry size 0x2C | |
| +0x10 | u32 0x40: size of the second table's entries | |
| +0x14 | u32 **sound count** (705) | |
| +0x20 | u64 file size | equals the file |
| +0x28 | u64 **entries offset** (0xE50000) | |
| +0x30 | u64 second table offset (0xE58000): 0x40 bytes per sound, random-looking (hashes?) | *unknown* |
| +0x38 | 16 bytes, a GUID | |

## Entry (0x2C bytes)

| Off | Field |
|---|---|
| +0x00 | u32 sound id (hash) |
| +0x04 | u32 byte size of the packets |
| +0x08 | u32 byte size of the packet table (4 per packet) |
| +0x0C | u32 sample count per channel (the playable length) |
| +0x14 | u32 file offset of the packet table; the packets follow it |
| +0x1C | u32 sample rate (48,000 for all 705) |
| +0x20 | u8 channels (1 or 2; equals the Opus stereo bit of every sound) |
| +0x22 | u8 codec: 14 = Opus (every sound measured) |
| +0x24 | 8 bytes, *unknown* |

## Audio

The packet table holds one u32 offset per packet (relative to the first packet); each packet is `{u16 length,
Opus packet}` and decodes to 960 samples (20 ms at 48 kHz). Measured on all 705 sounds: every length prefix equals
its packet's size minus 2, and the decoded length exceeds the stored sample count by 960–1,919 samples (the
encoder's lead-in and padding; the reader keeps the first `+0x0C` samples).

## Aliases (soundbank asset, 0x200 bytes; loader 142EB6360)

+0x20 u64 count, +0x28 array of 0x20-byte **alias lists** (142E68EC0): `{name, u32 hash, entries, u32 count}`.
Each **entry** (0x20, 142E68C50): `{file name, u32 sound id (+0x08), u32 (+0x0C), record (+0x10), params (+0x18)}`;
the record is 0x28 bytes of names (142E69120: strings at +0x00, +0x08, +0x18, +0x20), the params 0xB0 bytes
(floats such as 1.0, 5000, 25000: volume and distance values, *not named yet*).

Measured on `mp_t_gun_course.all`: 894 aliases with 17,078 entries naming 2,470 distinct sound ids. **All 705 ids
of `mp_t_gun_course.sabs` are among them** (2,282 entries); the rest are in the common and language banks
(`englisheng_mp_t_gun_course.sabs` and others not uploaded yet). File names look like
`ambient\amb_mp_quarry_interior_lr.SL.75.36000.all`. `tools/assets/sabs.py` `read_aliases` reads them.
