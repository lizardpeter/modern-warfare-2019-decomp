# Sound (`.sabs` banks)

Audio is in `.sabs` files (5,629 in the install; 1,074 in the uploaded archives), per map, mode and language
(`mp_t_gun_course.sabs`, `englisheng_mp_t_gun_course.sabs`, `patch_…`). Measured on `mp_t_gun_course.sabs`
(15,155,328 bytes, 705 sounds); read by `tools/assets/sabs.py`. Status: **all 705 sounds decode**; how the zone's
`soundbank` aliases name them (ids, volumes, variations) is not yet decoded.

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
