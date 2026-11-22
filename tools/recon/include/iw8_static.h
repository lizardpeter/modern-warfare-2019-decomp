// Static data in the hybrid build.
//
// Build environment, not game source. A `static` variable in the original (file scope or inside a
// function) lives at a fixed address in the original binary, but it has no public symbol, so it can't
// be linked by name like globals can. While the reconstruction is tested against the original, it
// must read and write that same storage. So reconstructed code declares original statics like this:
//
//     #define IW8_SOURCE "universal/com_math.cpp"   // once per file: the PDB source path
//
//     IW8_STATIC unsigned int holdrand IW8_AT("", "holdrand");
//     IW8_STATIC const float sRGBtoXYZ[4][4] IW8_AT("", "sRGBtoXYZ") IW8_INIT(= { ... });
//
//     int BoxOnPlaneSide(...)
//     {
//         IW8_STATIC int bops_initialized IW8_AT("BoxOnPlaneSide", "bops_initialized");
//
// IW8_AT(scope, name): scope is "" for a file static, or the enclosing function's name.
// tools/build_recon.py resolves every such symbol to the address in analysis/<build>/pdb/statics.tsv.
// IW8_INIT keeps the original initializer readable in the source; in the hybrid build the original
// binary's storage already holds it.
#pragma once

#define IW8_STATIC extern
#define IW8_AT(scope, name) __asm__("iw8s@" IW8_SOURCE "@" scope "@" name)
#define IW8_INIT(...)
