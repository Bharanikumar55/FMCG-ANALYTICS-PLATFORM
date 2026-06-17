export default function ResultsTable({ columns, results, rowCount }) {
  if (!columns?.length || !results?.length) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-white p-6 text-center">
        <p className="text-sm text-slate-400">Query results will appear here.</p>
      </div>
    );
  }

  const displayRows = results.slice(0, 100);

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
        <h3 className="text-sm font-semibold text-slate-700">Results</h3>
        <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
          {rowCount} row{rowCount !== 1 ? 's' : ''}
          {results.length > 100 && ' (showing first 100)'}
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-100 text-sm">
          <thead className="bg-slate-50">
            <tr>
              {columns.map((col) => (
                <th
                  key={col}
                  className="whitespace-nowrap px-4 py-2.5 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {displayRows.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-50/80">
                {columns.map((col) => (
                  <td key={col} className="whitespace-nowrap px-4 py-2 text-slate-700">
                    {row[col] === null || row[col] === undefined ? '—' : String(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
