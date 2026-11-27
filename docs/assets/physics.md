# Physics and collision (physicsasset, col_map)

Status: containers located; the Havok data needs its type compendium, which no uploaded zone contains.

## physicsasset (0x58 bytes; loader 142E68300)

+0x08 points to a **Havok 2018.2 binary tagfile** of `u32 +0x10` bytes (`SDKV` = `20180200`), measured on
`ammo_box_01` in `mp_t_gun_course` (2,324 bytes):

```
TAG0 2324
  SDKV 16     "20180200"
  DATA 1688   object data
  TCRF 32     type compendium reference: id 40354C32492E6BC1
  INDX 580
    ITEM 332  objects (type index, offset, count)
    PTCH 240  pointer patches
```

There is no `TYPE` section: the types are in a separate **type compendium** (`TCM0`), referenced by the 8-byte id
in `TCRF`. The exe holds only Havok's own tag names (`TAG0`, `TCM0`, … near file offset 0x7722640), not a
compendium. The likely holder is the `physicslibrary` asset (type 0), which none of the 13,653 zones read so far
contains: it should be in the common zones, whose patches are in archives not uploaded yet. +0x20, +0x28, +0x38,
+0x40 are arrays of `u32 +0x18` entries (4, 4, 8, 8 bytes) beside the tagfile: *meaning unknown*.

## col_map (0xF8 bytes; loader 142E88750)

Measured on `mp_t_gun_course`: +0x10 points to `{u32 count (337), ptr}`: 0x28-byte entries
`{u64, xmodel, physicsasset, u64 count, ptr}` linking placed models to their physics; +0x18 the map_ents;
+0x80..+0x94 two 3 × f32 vectors (−30,720, −31,744, −14,336 and 34,816, 33,792, 51,200: the collision bounds);
+0xC0 bytes and +0xD0 0x20-byte entries (count +0xC8 = 6). Static world collision is not a separate mesh here: it
comes from physics assets (Havok), so it waits on the compendium too.
