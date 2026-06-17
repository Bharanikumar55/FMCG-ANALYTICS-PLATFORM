export default function Sidebar({
  history,
  activeSessionId,
  onSelectHistory,
  onNewChat,
  isOpen,
  onClose,
}) {
  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-30 flex w-72 flex-col border-r border-slate-200 bg-white transition-transform lg:static lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between border-b border-slate-100 p-4">
          <div>
            <h2 className="text-sm font-bold text-slate-800">Query History</h2>
            <p className="text-xs text-slate-400">Past conversations</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded p-1 text-slate-400 hover:bg-slate-100 lg:hidden"
            aria-label="Close sidebar"
          >
            ✕
          </button>
        </div>

        <button
          type="button"
          onClick={onNewChat}
          className="mx-4 mt-4 rounded-lg border border-brand-200 bg-brand-50 px-4 py-2.5 text-sm font-medium text-brand-700 transition hover:bg-brand-100"
        >
          + New Conversation
        </button>

        <div className="flex-1 overflow-y-auto p-3">
          {history.length === 0 ? (
            <p className="px-2 py-4 text-center text-xs text-slate-400">No queries yet</p>
          ) : (
            <ul className="space-y-1">
              {history.map((item) => (
                <li key={item.id}>
                  <button
                    type="button"
                    onClick={() => onSelectHistory(item)}
                    className={`w-full rounded-lg px-3 py-2.5 text-left transition ${
                      activeSessionId === item.session_id
                        ? 'bg-brand-50 text-brand-800'
                        : 'text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <p className="line-clamp-2 text-sm font-medium">{item.user_question}</p>
                    <p className="mt-1 text-xs text-slate-400">
                      {new Date(item.created_at).toLocaleString()}
                      {item.success ? '' : ' · Failed'}
                    </p>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>
    </>
  );
}
