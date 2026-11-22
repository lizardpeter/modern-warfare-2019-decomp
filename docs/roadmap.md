# Roadmap

Planned work, in order. Enhanced-build features are listed with what must be decompiled first; `enhanced/` and
`records/patches.tsv` are created with the first enhancement.

## Now

1. **Ghidra pipeline on the decrypted image** (docs/arxan.md). Then check function coverage against `.pdata`
   (126,634 entries) and identify the high-entropy ranges left in `.text`.
2. **Names without symbols**: the asset-type table (146F1D670), dvar registrations, console commands, script
   function tables, Lua bindings and assert/log strings give names to large parts of the exe. Record each in
   records/names.tsv with method and evidence. Look for a symbol build of any later IW engine title as a reference.
3. **Asset formats** (docs/assets.md): containers first (CASC, zones, `.xpak`), then weapons, animations, models,
   textures, materials, audio, effects, movement, maps, each feeding the Forge (Rust-test) importer.
4. **Faithful decomp**, function by function with differential tests, starting with self-contained code
   (string and math utilities) to prove the harness on this build, then the asset loaders and movement code that
   the asset work needs anyway.

## Enhanced build (later)

Carry over what the other decomps settled on, each needing its code decompiled first:

- No connection to official servers (Demonware, Battle.net services, Ricochet); own server later. Needs the online
  layer mapped first.
- Low-latency input and presentation: raw input with no acceleration or smoothing, high DPI/polling handled,
  MW2019-style sensitivity (this is the game the user's sensitivity setup comes from), late latch, no V-Sync,
  uncapped frame rate decoupled from game logic. Needs the input, frame and present paths.
- Renderer: native Vulkan replacing D3D12 (no translation layer), NVIDIA Reflex. Needs the D3D12 renderer mapped.
- Security fixes from records/bugs.tsv and docs/security.md.
