# Assets

Goal: decode every IW8 asset format completely, from the code that reads it, so `lizardpeter/Rust-test` (Forge) can
import weapons, animations, models, textures, materials, audio, effects, movement characteristics and maps, the way
ghosts-decomp did for IW6 (its docs/fastfiles.md and docs/assets/).

Rules (as in ghosts-decomp):

- Every rule in `docs/assets/<kind>.md` names the function (address in ModernWarfare_BNet) it comes from, or says
  "measured on <file>"; anything else is *unverified*. Community format knowledge (docs/prior-art.md) is a lead to
  check against the code, never a source on its own.
- The reference readers in `tools/assets/` are plain Python. They are checked against the game itself: the exe's own
  loader run in the emulator on the same file must produce the same bytes (tests/assets/).
- The Forge importer is a port of these readers. IW8-specific code stays inside that importer; it translates into
  Forge's universal model, animation, material, audio and weapon formats rather than replaying IW8 at runtime.

## Where the data is

The install is Battle.net CASC (`.build.info`, `Data/`), not loose fastfiles. Inside it, IW8 keeps zones (fastfiles)
and streamed `.xpak` packages; the exe has the `.xpak` strings at 146F37CA8 onward. The data files are still being
uploaded to R2; the first step once they land is a CASC reader (`tools/assets/casc.py`) that lists and extracts
files by name, verified against `.build.info`'s build key.

Order of work:

1. **Containers**: CASC → zone files → the zone loader (decompression with Oodle, block layout, the asset pointer
   fix-ups) → `.xpak` streamed data (index, compressed blocks, hashed keys). Find `DB_LoadXFile`'s IW8 equivalent from
   the asset-type table below and its callers.
2. **Asset headers**: the per-type struct each loader reads (sizes from the pool table, fields from the load
   functions), written into `docs/assets/<kind>.md`.
3. **Payloads**, in the order Forge needs them (below).

## Asset types

The XAssetType enum, from the name table at 146F1D670 (122 entries; each type's default asset name follows the table
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
