# Effects (vfx, type 44)

An effect is a set of emitters, each a list of particle **modules** run at three stages: when a particle is born
(init), every frame (update), and tests that start another effect. Modules carry their parameters inline and
their animation as **graphs** (piecewise-linear curves over the particle's life). Reader: `tools/assets/vfx.py`.

Measured on `mp_t_gun_course.ff`: 1,516 effects, 457 with emitters, 12,520 modules, 40,072 graph segments.

## Header (0x40 bytes; loader 142E08300)

| Offset | Field |
|---|---|
| +0x00 | name |
| +0x08 | emitters, 0xA0 bytes each |
| +0x10 | a second array (loaders 142E72850 / 142E73C20, count u32 +0x20); *unverified* meaning |
| +0x1C | u32 emitter count |

## Emitter (0xA0 bytes; loader 142E06150)

+0x00 states, 0x20 bytes each (142E08250), count u32 +0x08 (1 in every emitter measured). A state's +0x00 points to
0x30 bytes holding three module lists `{pointer, u32 count}` of 0xF0-byte elements (142E066F0):

| Offset | Stage | Module types measured |
|---|---|---|
| +0x00 | init (at birth) | 0–31 |
| +0x10 | update (every frame) | 35–57 |
| +0x20 | tests | 58, 60, 62, 64 |

The rest of the emitter record (spawn counts and ranges, flags, the +0x50 struct loaded by 142E06000) is not yet
named.

## Module element (0xF0 bytes)

+0x00 s16 module type; +0x02..+0x0F zero in every file measured (runtime state); +0x10 the module body, a union
selected by the type (dispatch 142E07470).

Type names and body sizes are the exe's own table at **1476DD3B0** (0x30 bytes per type: +0x00 body size, +0x08
name, +0x18 the birth function, +0x28 the update function). Each size equals what the loader for that type reads.

| Types | Names |
|---|---|
| 0–33 | InitAtlas, InitAttributes, InitBeam, InitCameraOffset, InitCloud, InitDecal, InitFlare, InitGeoTrail, InitKillWrapBox, InitLightOmni, InitLightSpot, InitMaterial, InitMirrorTexture, InitModel, InitOcclusionQuery, InitOrientedSprite, InitParticleSim, InitPivot, InitPlayerFacing, InitRelativeVelocity, InitRotation, InitRotation3D, InitRunner, InitSound, InitSpawn, InitSpawnShapeBox, InitSpawnShapeCylinder, InitSpawnShapeEllipsoid, InitSpawnShapeMesh, InitSpawnShapeSphere, InitTail, InitVectorField, InitVolumetric, InitDismember |
| 34–57 | Attractor, AttractorGraph, ColorGraph, ColorLerp, EmissionGraph, EmissiveGraph, ShaderGraph, Force, ForceGraph, ForceDragGraph, Gravity, IntensityGraph, TemperatureGraph, ParentVelocityGraph, PhysicsLight, PhysicsRayCast, PositionGraph, RotationGraph, RotationGraph3D, ScaleByDistance, SizeGraph, SizeLerp, VelocityGraph, VectorFieldGraph |
| 58–64 | TestAge, TestBirth, TestDeath, TestGravity, TestImpact, TestPos, TestTimeInState |

Most common on the gun course: InitSpawn 1,459, InitAttributes 1,337, InitRelativeVelocity 851, InitMaterial 774,
SizeGraph 697, Gravity 704, ColorGraph 573.

### Graphs

A graph is `{pointer, u32 count}` to 16-byte keys (array loader 142E06080): `{f32 time, f32 value, f32 1/(time −
previous time), pad}`, time 0..1. The third value is 0 on the first key and equals the reciprocal of the preceding
interval on every other key (all 40,072 segments measured), so evaluation is `v0 + (t − t0)·(v1 − v0)·inv_dt`.
Graph arrays per type (offsets in the body; from each type's loader):

| Type | Offset, graphs | Type | Offset, graphs |
|---|---|---|---|
| InitAtlas | +0x20, 2 | ColorGraph | +0x10, 8 |
| InitFlare | +0x50, 4 | EmissionGraph | +0x10, 2 |
| InitSpawn | +0x10, 1 | EmissiveGraph | +0x10, 10 |
| InitSpawnShapeBox | +0x60, 6 | ShaderGraph | +0x10, 12 |
| InitSpawnShapeCylinder | +0x50, 5 | ForceGraph | +0x30, 6 |
| InitSpawnShapeEllipsoid | +0x50, 6 | ForceDragGraph, IntensityGraph, TemperatureGraph, ParentVelocityGraph, RotationGraph, ScaleByDistance, VectorFieldGraph | +0x10, 2 |
| InitSpawnShapeSphere | +0x40, 4 | PositionGraph, RotationGraph3D, SizeGraph, VelocityGraph | +0x10, 6 |
| AttractorGraph | +0x30, 8 | | |

Graph counts are even except InitSpawn and InitSpawnShapeCylinder (e.g. SizeGraph's 6, ColorGraph's 8), so
graphs are read in pairs, consistent with a min and a max curve the game picks between per particle
(*unverified*: the update functions are not read yet). Measured on the gun course: of 10,563 pairs,
5,908 are identical (no spread), 1,757 share their key times but not their values, and 2,898 have different key
times, so each curve of a pair must be evaluated on its own.

### Assets used by modules

A module that references assets has a list `{pointer, u32 count}` of 0x20-byte entries (142E06400); what an entry
holds depends on the owning module's type (142E06230):

| Module | List offset | Entry |
|---|---|---|
| InitMaterial | +0x10 | material (Load_MaterialPtr 142E84A90) |
| InitModel, InitSpawnShapeMesh | +0x10, +0x38 | xmodel (142EA5610) |
| InitDecal | +0x10 | three materials (142E064C0) |
| InitLightOmni, InitLightSpot | +0x08 | lightdef (142E7B610) |
| InitParticleSim | +0x08 | particlesimanimation (142EB5A90) |
| InitSound | +0x10 | sound alias name, a string (142E45CC0), e.g. `shell_eject_20mm` |
| InitVectorField | +0x08 | vectorfield (142E74EB0) |
| PhysicsLight | +0x10 | physicsfxpipeline and physicsfxshape (142E081E0) |
| InitBeam, InitRunner, Test* | +0x60, +0x50, +0x58 | another effect (Load_VfxPtr 142E08450) |

InitSpawnShapeMesh also has 16-byte entries at +0x48, counted by u32 body +0x30.

Measured on the gun course: 931 materials, 420 models, 256 sounds, 242 physics pipelines, 149 effects, 51 lights,
10 vector fields; every reference names an asset of the expected type.

## For Forge

An importer can already rebuild each emitter's module stack, its graphs, and the materials and models it draws.
Still needed for faithful playback: the meaning of each module's inline parameters, read from the birth and update
functions in the table (e.g. InitAttributes 146E021C0 adds a vec4 at +0x30 of its module argument to a per-particle attribute, *unverified* whether that argument is the element or the body;
InitSpawn 146E029E0 picks positions from the table at 147667C00), and the emitter record.
