// Commit the decompiler's own parameter and return types for every function in the given ranges, so that their
// callers are decompiled with the right argument lists.
// Args: <passes> <start end> [<start end> ...]  (hex VAs, end exclusive)
//
// Why: without committed signatures the decompiler guesses each call's arguments from the caller alone, and in the
// zone loaders it drops arguments that are still in a register from an earlier statement: 459 of the 8,393 calls in
// the loaders reachable from Load_XAssetList pass fewer arguments than the callee takes, e.g. `FUN_143760b30()` for
// Load_XStringCustom(char **) after a -2 string marker (docs/assets/loader-translation.md). The loader translator
// runs the decompiled C, so those calls must be complete. Runs inside a -readOnly decompile session: the changes
// only affect that session's decompilation.
//@category IW8
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.HighFunctionDBUtil;
import ghidra.program.model.pcode.HighFunctionDBUtil.ReturnCommitOption;
import ghidra.program.model.symbol.SourceType;

public class CommitSignatures extends GhidraScript {
	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		int passes = Integer.parseInt(args[0]);
		AddressSet set = new AddressSet();
		for (int k = 1; k + 1 < args.length; k += 2) {
			set.add(toAddr(Long.parseUnsignedLong(args[k], 16)), toAddr(Long.parseUnsignedLong(args[k + 1], 16) - 1));
		}
		DecompInterface ifc = new DecompInterface();
		ifc.setOptions(new DecompileOptions());
		ifc.toggleCCode(false);
		ifc.toggleSyntaxTree(true);
		ifc.setSimplificationStyle("decompile");
		if (!ifc.openProgram(currentProgram)) {
			throw new IllegalStateException("decompiler failed to open program: " + ifc.getLastMessage());
		}
		for (int pass = 1; pass <= passes; pass++) {
			int done = 0, failed = 0;
			FunctionIterator it = currentProgram.getFunctionManager().getFunctions(set, true);
			while (it.hasNext() && !monitor.isCancelled()) {
				Function f = it.next();
				DecompileResults r = ifc.decompileFunction(f, 60, monitor);
				HighFunction h = r == null ? null : r.getHighFunction();
				if (h == null) {
					failed++;
					continue;
				}
				int tx = currentProgram.startTransaction("commit signature");
				try {
					HighFunctionDBUtil.commitParamsToDatabase(h, true, ReturnCommitOption.COMMIT, SourceType.ANALYSIS);
					done++;
				} catch (Exception e) {
					failed++;
				} finally {
					currentProgram.endTransaction(tx, true);
				}
			}
			println(String.format("CommitSignatures pass %d: %d committed, %d failed", pass, done, failed));
		}
		ifc.dispose();
	}
}
