export default function ExecutiveSummary({ summary, error }) {
  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4">
        <h3 className="mb-2 text-sm font-semibold text-red-800">Error</h3>
        <p className="text-sm text-red-700">{error}</p>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-white p-4">
        <p className="text-sm text-slate-400">Executive summary will appear here after you ask a question.</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-brand-100 bg-gradient-to-br from-brand-50 to-white p-4 shadow-sm">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-lg">📊</span>
        <h3 className="text-sm font-semibold text-brand-900">Executive Summary</h3>
      </div>
      <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-700">{summary}</p>
    </div>
  );
}
