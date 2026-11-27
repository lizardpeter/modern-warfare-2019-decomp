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
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

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
		List<Function> order = new ArrayList<>();
		Set<Function> seen = new HashSet<>();
		FunctionIterator all = currentProgram.getFunctionManager().getFunctions(set, true);
		while (all.hasNext()) {
			postOrder(all.next(), set, seen, order);
		}
		for (int pass = 1; pass <= passes; pass++) {
			int done = 0, failed = 0;
			for (Function f : order) {
				if (monitor.isCancelled()) {
					break;
				}
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

	/** Callees (inside the ranges) before the function itself; iterative, as call chains can be deep. */
	private void postOrder(Function root, AddressSet set, Set<Function> seen, List<Function> order) {
		if (!seen.add(root)) {
			return;
		}
		List<Object[]> stack = new ArrayList<>();
		stack.add(new Object[] { root, new ArrayList<>(root.getCalledFunctions(monitor)).iterator() });
		while (!stack.isEmpty()) {
			Object[] top = stack.get(stack.size() - 1);
			@SuppressWarnings("unchecked")
			java.util.Iterator<Function> it = (java.util.Iterator<Function>) top[1];
			if (it.hasNext()) {
				Function c = it.next();
				if (set.contains(c.getEntryPoint()) && seen.add(c)) {
					stack.add(new Object[] { c, new ArrayList<>(c.getCalledFunctions(monitor)).iterator() });
				}
			} else {
				order.add((Function) top[0]);
				stack.remove(stack.size() - 1);
			}
		}
	}
}
