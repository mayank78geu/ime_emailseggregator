/**
 * RecordsPage — paginated table of all processed emails saved in MySQL
 */
import { useState, useEffect } from 'react';
import { getAllRecords } from '../api/shippingApi';
import CategoryBadge from '../components/CategoryBadge';

const PAGE_SIZE = 20;

function formatDate(dt) {
  if (!dt) return '—';
  const d = new Date(dt);
  return d.toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' });
}

export default function RecordsPage() {
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecords = async (pg = 0) => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAllRecords(pg * PAGE_SIZE, PAGE_SIZE);
      setData(res.data || []);
      setTotal(res.total || 0);
    } catch (e) {
      setError('Could not load records. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords(page);
  }, [page]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-1">
            Email <span className="text-gradient">Records</span>
          </h1>
          <p className="text-slate-400 text-sm">All processed emails saved to the database.</p>
        </div>
        <div className="glass-card px-5 py-3 text-center">
          <div className="text-2xl font-bold text-white">{total}</div>
          <div className="text-xs text-slate-500">Total Emails</div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="glass-card p-4 mb-6 border-l-4 border-l-red-500/60">
          <p className="text-sm text-red-400">⚠ {error}</p>
        </div>
      )}

      {/* Table */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5">
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">ID</th>
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">Filename</th>
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">Category</th>
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">Date Processed</th>
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">Preview</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i} className="border-b border-white/3">
                    {Array.from({ length: 5 }).map((_, j) => (
                      <td key={j} className="px-5 py-4">
                        <div className="h-4 rounded bg-white/5 animate-pulse shimmer-bg"></div>
                      </td>
                    ))}
                  </tr>
                ))
              ) : data.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-5 py-16 text-center text-slate-500">
                    <div className="text-4xl mb-3">📭</div>
                    <p>No records yet. Extract some emails first!</p>
                  </td>
                </tr>
              ) : (
                data.map((rec, i) => (
                  <tr
                    key={rec.id}
                    className="border-b border-white/3 hover:bg-white/3 transition-colors duration-150 animate-fade-in"
                    style={{ animationDelay: `${i * 30}ms` }}
                  >
                    <td className="px-5 py-4">
                      <span className="font-mono text-xs text-slate-500">#{rec.id}</span>
                    </td>
                    <td className="px-5 py-4">
                      {rec.filename ? (
                        <span className="flex items-center gap-1.5 text-slate-300">
                          📎 <span className="font-medium">{rec.filename}</span>
                        </span>
                      ) : (
                        <span className="text-slate-500 italic text-xs">pasted text</span>
                      )}
                    </td>
                    <td className="px-5 py-4">
                      {rec.category ? (
                        <CategoryBadge category={rec.category} />
                      ) : (
                        <span className="text-slate-600 text-xs">—</span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-slate-400 text-xs font-mono">
                      {formatDate(rec.upload_date)}
                    </td>
                    <td className="px-5 py-4">
                      <span className="text-xs text-slate-500 font-mono truncate max-w-[200px] inline-block">
                        {rec.raw_content?.slice(0, 60)}…
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {total > PAGE_SIZE && (
          <div className="flex items-center justify-between px-5 py-4 border-t border-white/5">
            <span className="text-xs text-slate-500">
              Page {page + 1} of {totalPages} · {total} total
            </span>
            <div className="flex gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage((p) => p - 1)}
                className="btn-secondary text-xs px-3 py-1.5 disabled:opacity-30"
              >
                ← Prev
              </button>
              <button
                disabled={page >= totalPages - 1}
                onClick={() => setPage((p) => p + 1)}
                className="btn-secondary text-xs px-3 py-1.5 disabled:opacity-30"
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
