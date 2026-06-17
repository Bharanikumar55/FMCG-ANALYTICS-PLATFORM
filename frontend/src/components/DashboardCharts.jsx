import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899'];

function detectChartType(columns, results) {
  if (!results?.length || !columns?.length) return null;

  const numericCols = columns.filter((col) =>
    results.some((row) => typeof row[col] === 'number' || !Number.isNaN(Number(row[col])))
  );
  const labelCol = columns.find((col) => !numericCols.includes(col)) || columns[0];
  const valueCol = numericCols.find((col) => col !== labelCol) || numericCols[0];

  if (!valueCol) return null;

  const data = results.slice(0, 12).map((row) => ({
    name: String(row[labelCol] ?? '').slice(0, 20),
    value: Number(row[valueCol]) || 0,
  }));

  return { data, labelCol, valueCol, isTimeSeries: labelCol.toLowerCase().includes('date') };
}

export default function DashboardCharts({ columns, results }) {
  const chartInfo = detectChartType(columns, results);

  if (!chartInfo) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-white p-6 text-center">
        <p className="text-sm text-slate-400">Charts will auto-generate from query results.</p>
      </div>
    );
  }

  const { data, valueCol, isTimeSeries } = chartInfo;

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-slate-700">
          {isTimeSeries ? 'Trend' : 'Bar Chart'} — {valueCol}
        </h3>
        <ResponsiveContainer width="100%" height={240}>
          {isTimeSeries ? (
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#22c55e" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          ) : (
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#22c55e" radius={[4, 4, 0, 0]} />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-slate-700">Distribution — {valueCol}</h3>
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
              labelLine={false}
            >
              {data.map((_, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend wrapperStyle={{ fontSize: 11 }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
