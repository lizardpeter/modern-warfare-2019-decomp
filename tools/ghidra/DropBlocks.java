// Pre-analysis script: remove whole memory blocks that are not the game's code before auto-analysis, so the
// analyzers never spend time on them. Arguments: pairs of hex VAs `start end` (end exclusive), from a build's
// `exclude` list in target.toml when the build sets `ghidra_drop_excluded = true`.
//
// MW2019's Arxan section (the second .text, 113 MB) is as large as the game's own code; BO3 analysed its Arxan
// section and then excluded the 333k fragments from the published tables. Here it is removed up front to halve the
// analysis time. Arxan's calls and jumps from game code then point at missing memory, which is what they are:
// not game code. Each range must cover whole blocks exactly; anything else aborts.
//@category IW8
import ghidra.app.util.headless.HeadlessScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;

public class DropBlocks extends HeadlessScript {
	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		if (args.length % 2 != 0) {
			printerr("DropBlocks: expected pairs of start/end VAs");
			setHeadlessContinuationOption(HeadlessContinuationOption.ABORT_AND_DELETE);
			return;
		}
		Memory mem = currentProgram.getMemory();
		for (int i = 0; i < args.length; i += 2) {
			Address start = toAddr(Long.parseUnsignedLong(args[i], 16));
			long end = Long.parseUnsignedLong(args[i + 1], 16);
			MemoryBlock b = mem.getBlock(start);
			if (b == null || !b.getStart().equals(start) || b.getEnd().getOffset() + 1 != end) {
				printerr(String.format("DropBlocks: %s-%x is not exactly one block (%s)", args[i], end,
						b == null ? "none" : b.getName() + " " + b.getStart() + "-" + b.getEnd()));
				setHeadlessContinuationOption(HeadlessContinuationOption.ABORT_AND_DELETE);
				return;
			}
			println(String.format("DropBlocks: removing %s %s-%s (%d bytes)", b.getName(), b.getStart(), b.getEnd(),
					b.getSize()));
			mem.removeBlock(b, monitor);
		}
	}
}
