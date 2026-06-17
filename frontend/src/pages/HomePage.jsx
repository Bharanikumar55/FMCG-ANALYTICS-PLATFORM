import { useCallback, useEffect, useState } from 'react';
import { checkHealth, exportResults, getHistory, sendChatMessage } from '../api';
import ChatWindow from '../components/ChatWindow';
import DashboardCharts from '../components/DashboardCharts';
import ExecutiveSummary from '../components/ExecutiveSummary';
import ResultsTable from '../components/ResultsTable';
import Sidebar from '../components/Sidebar';
import SQLViewer from '../components/SQLViewer';

function generateSessionId() {
  return `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

export default function HomePage() {
  const [sessionId, setSessionId] = useState(generateSessionId);
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [health, setHealth] = useState(null);

  const [currentSql, setCurrentSql] = useState('');
  const [results, setResults] = useState([]);
  const [columns, setColumns] = useState([]);
  const [rowCount, setRowCount] = useState(0);
  const [summary, setSummary] = useState('');
  const [error, setError] = useState('');

  const loadHistory = useCallback(async () => {
    try {
      const { data } = await getHistory();
      setHistory(data);
    } catch {
      /* optional on first load */
    }
  }, []);

  useEffect(() => {
    checkHealth()
      .then(({ data }) => setHealth(data))
      .catch(() => setHealth({ status: 'error', gemini_configured: false }));
    loadHistory();
  }, [loadHistory]);

  const handleSend = async (question) => {
    setLoading(true);
    setError('');
    setMessages((prev) => [...prev, { role: 'user', content: question }]);

    try {
      const { data } = await sendChatMessage(question, sessionId);

      if (data.success) {
        setCurrentSql(data.generated_sql || '');
        setResults(data.results || []);
        setColumns(data.columns || []);
        setRowCount(data.row_count || 0);
        setSummary(data.executive_summary || '');
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: data.executive_summary || 'Query completed successfully.' },
        ]);
      } else {
        setError(data.error_message || 'Query failed');
        setCurrentSql(data.generated_sql || '');
        setResults([]);
        setColumns([]);
        setRowCount(0);
        setSummary('');
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: `Error: ${data.error_message}` },
        ]);
      }
      await loadHistory();
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Request failed';
      setError(msg);
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${msg}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!currentSql) return;
    try {
      const { data } = await exportResults(currentSql);
      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `fmcg_export_${Date.now()}.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.detail || 'Export failed');
    }
  };

  const handleNewChat = () => {
    setSessionId(generateSessionId());
    setMessages([]);
    setCurrentSql('');
    setResults([]);
    setColumns([]);
    setRowCount(0);
    setSummary('');
    setError('');
    setSidebarOpen(false);
  };

  const handleSelectHistory = (item) => {
    setSessionId(item.session_id);
    setCurrentSql(item.generated_sql || '');
    setSummary(item.executive_summary || '');
    setError(item.error_message || '');
    setRowCount(item.row_count || 0);
    setResults([]);
    setColumns([]);
    setMessages([
      { role: 'user', content: item.user_question },
      {
        role: 'assistant',
        content: item.executive_summary || item.error_message || 'No summary available.',
      },
    ]);
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar
        history={history}
        activeSessionId={sessionId}
        onSelectHistory={handleSelectHistory}
        onNewChat={handleNewChat}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 shadow-sm">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
              aria-label="Open sidebar"
            >
              ☰
            </button>
            <div>
              <h1 className="text-base font-bold text-slate-800 sm:text-lg">FMCG Analytics</h1>
              <p className="text-xs text-slate-400">Conversational AI Platform</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {health && (
              <span
                className={`hidden rounded-full px-2.5 py-1 text-xs font-medium sm:inline ${
                  health.status === 'ok'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-yellow-100 text-yellow-700'
                }`}
              >
                {health.record_count?.toLocaleString()} records
                {!health.gemini_configured && ' · API key needed'}
              </span>
            )}
            {currentSql && (
              <button
                type="button"
                onClick={handleExport}
                className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:bg-slate-50"
              >
                Export CSV
              </button>
            )}
          </div>
        </header>

        <div className="flex flex-1 flex-col overflow-hidden lg:flex-row">
          <div className="flex h-1/2 flex-col border-b border-slate-200 bg-white lg:h-auto lg:w-2/5 lg:border-b-0 lg:border-r">
            <ChatWindow
              messages={messages}
              onSend={handleSend}
              loading={loading}
              onSuggestionClick={handleSend}
            />
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            <div className="mx-auto max-w-5xl space-y-4">
              <ExecutiveSummary summary={summary} error={error && !summary ? error : ''} />
              <SQLViewer sql={currentSql} />
              <ResultsTable columns={columns} results={results} rowCount={rowCount} />
              <DashboardCharts columns={columns} results={results} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
