// Stage B of the analysis (.github/workflows/ghidra.yml, job `switches`): run Ghidra's Decompiler Switch Analysis
// once over all executable memory of an already analysed, saved project, then let the post-scripts export again.
//
// Why a separate stage: on TU67 the full auto-analysis did not fit one job. The main analyzers ran 4.5 h, then the
// decompiler-driven switch analysis was still going when the 330-min step limit killed the job, leaving no export,
// no timing report and no project. Stage A (PrepAnalysis.java "two-stage") turns this analyzer off; this script runs
// it in a job of its own. The decompiler runs as native processes outside the JVM heap, so it gets more threads
// here than the single-thread limit stage A keeps for the heap-hungry constant-propagation analyzer.
//
// Argument: number of decompiler threads (default 3).
//@category IW8
import ghidra.app.plugin.core.analysis.AutoAnalysisManager;
import ghidra.app.services.Analyzer;
import ghidra.app.util.headless.HeadlessScript;
import ghidra.framework.options.Options;
import ghidra.program.model.listing.Program;

public class RunSwitchAnalysis extends HeadlessScript {
	static final String NAME = "Decompiler Switch Analysis";

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		int threads = args.length > 0 ? Integer.parseInt(args[0]) : 3;
		Options opts = currentProgram.getOptions(Program.ANALYSIS_PROPERTIES);
		opts.setBoolean(NAME, true);
		opts.setInt(NAME + ".Max Threads", threads);

		AutoAnalysisManager mgr = AutoAnalysisManager.getAnalysisManager(currentProgram);
		Analyzer analyzer = mgr.getAnalyzer(NAME);
		if (analyzer == null) {
			printerr("RunSwitchAnalysis: analyzer '" + NAME + "' not found");
			setHeadlessContinuationOption(HeadlessContinuationOption.ABORT);
			return;
		}
		int before = currentProgram.getFunctionManager().getFunctionCount();
		long t0 = System.currentTimeMillis();
		mgr.scheduleOneTimeAnalysis(analyzer, currentProgram.getMemory().getExecuteSet());
		mgr.startAnalysis(monitor);
		println(String.format("RunSwitchAnalysis: %s with %d threads took %.1f min; functions %d -> %d", NAME, threads,
				(System.currentTimeMillis() - t0) / 60000.0, before, currentProgram.getFunctionManager().getFunctionCount()));
		println(mgr.getTaskTimesString());
	}
}
