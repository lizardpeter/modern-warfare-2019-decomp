// Decompile one shard of the program's functions to JSONL.
// Args: <out.jsonl> <shard-index> <shard-count> [timeout-seconds]
//
// Fragments are written as {"va","name","skipped"} and not decompiled. A fragment is a Ghidra function whose entry
// lies strictly inside an x64 exception-directory entry (a real function's .pdata range) and that is reached only by
// jumps: no call and no data reference. MW2019's flattened code jumps into shared dispatcher blocks inside other
// functions (`mov [rsp+40h], <hash>; jmp <block>`); Ghidra makes those blocks functions, and decompiling one runs
// into the next function's bytes until the timeout. On TU67 they stalled every shard (docs/builds.md). Real leaf and
// tail-called functions are unaffected: they start an exception entry, are called, or are referenced as data.
//@category IW8
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.Writer;

import com.google.gson.JsonObject;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import java.util.Arrays;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

public class Decompile extends GhidraScript {
	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		File out = new File(args[0]);
		int shard = Integer.parseInt(args[1]);
		int shards = Integer.parseInt(args[2]);
		int timeout = args.length > 3 ? Integer.parseInt(args[3]) : 90;

		DecompInterface ifc = new DecompInterface();
		ifc.setOptions(new DecompileOptions());
		ifc.toggleCCode(true);
		ifc.toggleSyntaxTree(false);
		ifc.setSimplificationStyle("decompile");
		if (!ifc.openProgram(currentProgram)) {
			throw new IllegalStateException("decompiler failed to open program: " + ifc.getLastMessage());
		}

		long[][] pdata = exceptionEntries();
		println(String.format("shard %d: %d exception-directory entries", shard, pdata.length));

		int i = 0, ok = 0, failed = 0, skipped = 0;
		long t0 = System.currentTimeMillis();
		try (Writer w = new BufferedWriter(new FileWriter(out))) {
			FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
			while (it.hasNext()) {
				monitor.checkCancelled();
				Function f = it.next();
				if (f.isExternal() || f.isThunk() || (i++ % shards) != shard) {
					continue;
				}
				JsonObject o = new JsonObject();
				o.addProperty("va", String.format("%09X", f.getEntryPoint().getOffset()));
				o.addProperty("name", f.getName(true));
				String inside = fragmentOf(f, pdata);
				if (inside != null) {
					o.addProperty("skipped", "fragment: inside " + inside + ", jump references only");
					w.write(o.toString() + "\n");
					skipped++;
					continue;
				}
				long tf = System.currentTimeMillis();
				DecompileResults r = ifc.decompileFunction(f, timeout, monitor);
				long ms = System.currentTimeMillis() - tf;
				if (ms > 30000) {
					println(String.format("shard %d: slow %s %.1fs (%d bytes)", shard, o.get("va").getAsString(),
							ms / 1000.0, f.getBody().getNumAddresses()));
				}
				if (r != null && r.decompileCompleted() && r.getDecompiledFunction() != null) {
					o.addProperty("c", r.getDecompiledFunction().getC());
					ok++;
				}
				else {
					o.addProperty("error", r == null ? "null result" : r.getErrorMessage());
					failed++;
				}
				w.write(o.toString() + "\n");
				if ((ok + failed) % 1000 == 0) {
					println(String.format("shard %d: %d ok, %d failed, %d fragments skipped, %ds", shard, ok, failed, skipped,
							(System.currentTimeMillis() - t0) / 1000));
				}
			}
		}
		ifc.dispose();
		println(String.format("shard %d done: %d ok, %d failed, %d fragments skipped", shard, ok, failed, skipped));
	}

	/** Exception-directory entries {begin, end} as VAs, sorted, read through the PE header Ghidra maps at the image
	 *  base (DataDirectory[3]); empty for a program without one. */
	private long[][] exceptionEntries() throws Exception {
		Memory mem = currentProgram.getMemory();
		Address base = currentProgram.getImageBase();
		if (mem.getShort(base) != 0x5A4D) {
			return new long[0][];
		}
		Address pe = base.add(mem.getInt(base.add(0x3C)));
		if (mem.getInt(pe) != 0x4550 || mem.getShort(pe.add(0x18)) != 0x20B) {
			return new long[0][];   // not PE32+
		}
		Address dir = pe.add(0x18 + 0x70 + 3 * 8);
		long rva = mem.getInt(dir) & 0xFFFFFFFFL, size = mem.getInt(dir.add(4)) & 0xFFFFFFFFL;
		long b0 = base.getOffset();
		long[][] out = new long[(int) (size / 12)][];
		int n = 0;
		for (long o = 0; o + 12 <= size; o += 12) {
			Address e = base.add(rva + o);
			long b = mem.getInt(e) & 0xFFFFFFFFL, en = mem.getInt(e.add(4)) & 0xFFFFFFFFL;
			if (b != 0 && en > b) {
				out[n++] = new long[] { b0 + b, b0 + en };
			}
		}
		out = Arrays.copyOf(out, n);
		Arrays.sort(out, (x, y) -> Long.compare(x[0], y[0]));
		return out;
	}

	/** The exception entry (as "begin-end") a fragment lies strictly inside, or null if f is not a fragment. */
	private String fragmentOf(Function f, long[][] pdata) {
		long va = f.getEntryPoint().getOffset();
		int lo = 0, hi = pdata.length - 1, k = -1;
		while (lo <= hi) {
			int mid = (lo + hi) >>> 1;
			if (pdata[mid][0] <= va) { k = mid; lo = mid + 1; } else { hi = mid - 1; }
		}
		if (k < 0 || va == pdata[k][0] || va >= pdata[k][1]) {
			return null;
		}
		ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(f.getEntryPoint());
		boolean any = false;
		while (refs.hasNext()) {
			Reference r = refs.next();
			if (!r.getReferenceType().isJump()) {
				return null;   // called, or referenced as data: a real entry point
			}
			any = true;
		}
		return any ? String.format("%09X-%09X", pdata[k][0], pdata[k][1]) : null;
	}
}
