export default function SQLViewer({ sql }) {
  if (!sql) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-slate-900/5 p-4">
        <p className="font-mono text-xs text-slate-400">Generated SQL will appear here...</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-700 bg-slate-900 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-700 px-4 py-2">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Generated SQL</span>
        <button
          type="button"
          onClick={() => navigator.clipboard.writeText(sql)}
          className="rounded px-2 py-1 text-xs text-slate-400 transition hover:bg-slate-800 hover:text-white"
        >
          Copy
        </button>
      </div>
      <pre className="overflow-x-auto p-4 font-mono text-sm leading-relaxed text-emerald-400">
        <code>{sql}</code>
      </pre>
    </div>
  );
}
