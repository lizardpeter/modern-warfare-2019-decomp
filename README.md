# modern-warfare-2019-decomp

Decompilation of Call of Duty: Modern Warfare (2019) (IW8, PC, x64, Battle.net title update 67, with the 1.63 install's data), and a complete, verified
description of its asset formats for the Forge engine's importer.

- **AGENTS.md**: rules, layout, status ladder. Read it first.
- **STATUS.md**: progress (generated).
- **docs/builds.md**: the builds and their provenance. **docs/arxan.md**: how the protected exe is decrypted.
- **docs/assets.md**: the asset-format plan and the XAssetType list. **docs/roadmap.md**: what comes next.

Game files are never committed; `target.toml` lists them by R2 key and sha256. The Ghidra analysis runs in GitHub
Actions (`.github/workflows/ghidra.yml`) and is committed under `analysis/`.
