# Raw files and compiled scripts

Measured on `mp_t_gun_course`; read by `tools/assets/rawfile.py`.

## rawfile (0x18 bytes; loader 142E7C0B0)

`{name, u32 compressed size, u32 size, data}`; the data is zlib (`78 DA`). Measured: all 6 raw files of
`mp_t_gun_course` inflate to exactly their size: `.gsc` source text, an animation tree (`animtrees/cloth.atr`), a
`.vision` file. The vision file's keys are obfuscated (`NONMKTKNNM "mp_donetsk_clut"`): letters standing for a
hash, *not decoded*.

## scriptfile (0x28 bytes; loader 142E745B0)

`{name, …, u32 compressed size (+0x08), u32 size (+0x0C), u32 bytecode size (+0x10), compressed section (+0x18),
bytecode (+0x20)}`. The section inflates (zlib) to exactly +0x0C bytes (60 scripts measured); it starts with u32
counts and holds the script's strings encrypted (no readable names in it). The bytecode is stored as is. Decoding
the section and the bytecode (GSC) is *not done*; many scripts are named by number (`1688`, `58121`, …), i.e. by
id, not path.
