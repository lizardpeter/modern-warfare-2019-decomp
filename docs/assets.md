# Assets

Goal: decode every IW8 asset format completely, from the code that reads it, so `lizardpeter/Rust-test` (Forge) can
import weapons, animations, models, textures, materials, audio, effects, movement characteristics and maps, the way
ghosts-decomp did for IW6 (its docs/fastfiles.md and docs/assets/).

Rules (as in ghosts-decomp):

- Every rule in `docs/assets/<kind>.md` names the function (address in ModernWarfare_TU67) it comes from, or says
  "measured on <file>"; anything else is *unverified*. Community format knowledge (docs/prior-art.md) is a lead to
  check against the code, never a source on its own.
- The reference readers in `tools/assets/` are plain Python. They are checked against the game itself: the exe's own
  loader run in the emulator on the same file must produce the same bytes (tests/assets/).
- The Forge importer is a port of these readers. IW8-specific code stays inside that importer; it translates into
  Forge's universal model, animation, material, audio and weapon formats rather than replaying IW8 at runtime.

## Where the data is

The install is Battle.net CASC (`.build.info`, `Data/`). Zones are CASC files (`IWffa100`, Oodle-compressed);
streamed data is in `.xpak` packages. Containers are documented in docs/assets/zones.md:

- **CASC archives**: read (`tools/assets/casc_archive.py`); **every file by name** through the build config, local
  indices and TVFS (`tools/assets/casc.py`): 72,833 files, of which 58,726 zones, 4,910 `.xpak`, 5,629 `.sabs` sound
  banks and 2,934 `.fp` patches. The 1.63 install spans 163 archives (about 163 GB).
- **Fastfile patches**: a zone is its `.ff` plus, often, a `.fp` VCDIFF patch with two extensions (docs/assets/zones.md
  7), applied by `tools/assets/fastfile_patch.py` from the game's decoder 143F212C0, every window checksum verified.
- **Zones**: header, signed block and compressed stream read and checked against TU67's code; every zone at its
  current format version decompresses to its declared size (`tools/assets/zone.py`, with the game's own Oodle
  run in the emulator).
- **Asset list and headers**: the asset list is parsed, and every type's loader and header size is extracted from the
  code into analysis/ModernWarfare_TU67/assets/asset_types.tsv (114 of 122 types).
- **Whole zones load in the emulator with the game's own loaders** (tests/assets/zone_emu.py, docs/assets/zones.md
  8–9): the patched `mp_t_gun_course` loads to its last byte, 12,235 assets with their names. This is the ground truth
  for every per-type reader, and already lets any asset be inspected exactly as the game holds it in memory.
- **Zones load from the original files alone** with the translated loaders (tools/assets/loaders/, docs/assets/
  loader-translation.md): TU67's decompiled loaders run as Python and match the game's own code byte for byte on
  three character zones and the whole `mp_t_gun_course` map (tests/assets/loaders_check.py).
- **Layouts of every asset type in the traced zones** (docs/assets/layouts.md): every struct of every asset type in the traced zones, from
  the game's own loaders over 3,109 zones: sizes, pointers, counts, strings, asset references (451 structs, 55 types).
- **Animations**: the XAnimParts header and everything it points to are located (docs/assets/animations.md); the
  track encoding is next.

## Plan (priority: weapons, characters, animations, maps)

1. **Per type, from its loader**: the header and pointed-to layout (Load_<T> in asset_types.tsv), then the meaning
   of the fields from the code that uses them, each checked on assets the emulator loaded. Order: xanim, xmodel and
   xmodelsurfs (characters are xmodels: the `mp_bd_*` body and `mp_hd_*` head transient zones), weapon, attachment
   and camo, then the map assets (gfx_map, col_map, com_map, map_ents), image and material along the way.
2. **A stand-alone reader.** A zone has no index: reaching any asset means loading every asset before it, so a
   reader that runs without the game needs every type's loader (about 2,800 generated functions in TU67's
   142DF0000–142EC0000, far too many to port by hand as ghosts-decomp did with its PDB). The loaders are
   machine-generated and regular, so the plan is to translate them mechanically from the code into the Python
   reader (and the same description into the Forge importer), checked against the emulator byte for byte on whole
   zones. Until then, the emulator is the only complete walker.
3. **Streamed data** (`.xpak`: images, model surfaces, animations): after the zone readers.

Zones measured so far are those whose base and patch are in the archives present locally (data.000, .006, .016,
.017, .047): most zones are base files that need a `.fp` patch, and the patches are spread over the other archives
(`common_mp.fp`, which holds the multiplayer weapons, is in data.066).

## Asset types

The XAssetType enum, from the name table at 147627730 in TU67 (146F1D670 in TU63; identical, 122 entries; each type's default asset name follows the table
in the same order). Grouped by what Forge needs:

| Forge need | IW8 asset types (enum value) |
|---|---|
| Weapons | weapon (43), attachment (42), camo (99), reticle (86), tracer (58), laser (68), weapontrigger (118), equipsndtable (64), locdmgtable (94), bulletpenetration (95), triggereffect (117) |
| Characters | xmodel (9), xmodelsurfs (8), xcompositemodel (100), xmodelalias (50), character (49), clientcharacter (90), suit (70), accessory (93), clothasset (91), proceduralbones (84), dynamicbones (85), xmodeldetailcollision (101) |
| Animation | xanim (7), xanimcurve (87), animclass (38), playeranim (39), gesture (40), animpkg (77), suitanimpackage (71), blendspace2d (97), cinematicmotion (92), aianimset (82), aiasm (83), xcam (98) |
| Textures | image (19), streamkey (102), streaminginfo (67) |
| Materials and shaders | material (11), techset (18), computeshader (12), libshader (13), vertexshader (14), hullshader (15), domainshader (16), pixelshader (17), decalvolumematerial (111), decalvolumemask (112) |
| Audio | soundglobals (20), soundbank (21), soundbanktransient (22), soundbanklist (110), sfxpkg (78) |
| Effects | vfx (44), impactfx (45), surfacefx (46), vfxpkg (79), footstepvfx (80), particlesimanimation (66), vectorfield (65), physicsvfxeventasset (2), physicssfxeventasset (1) |
| Movement and physics | physicslibrary (0), physicsasset (3), physicsfxpipeline (4), physicsfxshape (5), playeranim (39), scriptbundle (96), keyvaluepairs (104); most movement values are dvars and string tables (see below) |
| Maps | col_map (23), com_map (24), glass_map (25), gfx_map (31), gfx_map_trzone (32), map_ents (29), addon_map_ents (60), fx_map (30), fx_map_trzone (114), lightdef (34), iesprofile (33), gradingclut (35), fogspline (37), stterrain (105), collisiontile (107), dynentitylist (113), navmesh (27), aipaths (26), tacgraph (28) |
| Data and script | stringtable (54), rawfile (51), scriptfile (52), luafile (62), ddl (57), localize (41), ttf (69), netconststrings (61), scriptable (63), dlogschema (115) |
| Other | mayhem (10), ui_map (36), aitype (47), mptype (48), vehicle (59), camera (72), hudoutline (73), spaceshiptarget (74), rumble (75), rumblegraph (76), behaviortree (81), coverselector (88), enemyselector (89), execution (108), carryobject (109), streamtreeoverride (103), nativescriptpatch (106), edgelist (116), dwidata (119), string (120), assetlist (121), physicsdebugdata (6), scriptdebugdata (53), leaderboarddef (55), virtualleaderboarddef (56) |

## What Forge needs from each

- **Weapons**: complete, server-side definitions (Forge rule: one fully usable asset, no visual-only split): fire
  rate, damage and falloff ranges, recoil, spread, ADS and sprint timings, reload and magazine data, attachments and
  what each changes, view and world models, the animation set, sounds, effects, camos. Forge's native M4 already
  uses MW2019 M4A1 values; this replaces hand-entered numbers with decoded ones.
- **Animations**: bone tracks with their compression decoded exactly (IW8 quantises rotations and translations;
  *unverified* until read from the code), notetracks, additive/delta flags, blend spaces and the animclass/playeranim
  state machine that picks them, retargeted to Forge's universal rig.
- **Models**: LODs, skinning (weights per vertex, bone hierarchy), vertex packing, composite models and accessories.
- **Textures**: image header and streamed mips at full resolution, format per channel kind (BCn), so Forge can keep
  its per-data-kind block formats.
- **Materials**: techset and shader constants, the texture slots, and the DXIL shaders, so each material can be
  represented faithfully (translated through Forge's universal IR to Slang/SPIR-V) and mapped to Forge's PBR
  material for the enhanced path.
- **Audio**: sound bank layout, codec (Opus/other; *unverified*), aliases with volume, falloff, spatial and occlusion
  settings, so Forge's audio engine can use them directly.
- **Effects**: vfx graphs (emitters, curves, materials, physics events) mapped to Forge's effect system.
- **Movement**: the player movement constants (speeds, acceleration, slide, mantle, jump, ADS move scale, sprint and
  tactical sprint) from the dvar table and the movement code itself (`PM_*` equivalents), decompiled faithfully so
  Forge can reproduce the feel exactly.
