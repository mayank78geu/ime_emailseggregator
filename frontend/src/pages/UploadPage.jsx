/**
 * UploadPage — paste email text or upload a file, see extracted records
 */
import { useState, useCallback } from 'react';
import { extractEmail, uploadFile } from '../api/shippingApi';
import RecordCard from '../components/RecordCard';

const SAMPLE_EMAIL = `MV SHENG AN HAI
DWT 56564 / OPEN XIAMEN / O/A 2ND JUNE
FLAG: PANAMA / BUILT: 2012
---
MV PACIFIC GLORY
DWT 32000 / OPEN SINGAPORE / O/A 5TH JUNE
FLAG: MARSHALL ISLANDS / BUILT: 2015`;

export default function UploadPage() {
  const [emailText, setEmailText] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('text'); // 'text' | 'file'
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState(null);

  const handleExtract = async () => {
    if (!emailText.trim()) return;
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const data = await extractEmail(emailText);
      setResults(data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to connect to API. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;
    setFileName(file.name);
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const data = await uploadFile(file);
      setResults(data.data || []);
    } catch (e) {
      setError(e.response?.data?.detail || 'File upload failed.');
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file);
  }, []);

  const stats = results
    ? {
        total: results.length,
        tonnage: results.filter((r) => r.category === 'TONNAGE').length,
        vc: results.filter((r) => r.category === 'CARGO_VC').length,
        tc: results.filter((r) => r.category === 'CARGO_TC').length,
        warnings: results.reduce((acc, r) => acc + (r._warnings?.length || 0), 0),
      }
    : null;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10 animate-fade-in">
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Email{' '}
          <span className="text-gradient">Extractor</span>
        </h1>
        <p className="text-slate-400 text-sm">
          Paste raw shipping email text or upload a file to extract structured data.
        </p>
      </div>

      {/* Mode toggle */}
      <div className="flex gap-2 mb-5">
        {['text', 'file'].map((m) => (
          <button
            key={m}
            onClick={() => { setMode(m); setResults(null); setError(null); setFileName(null); }}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
              mode === m
                ? 'bg-accent-blue text-white shadow-lg shadow-blue-500/20'
                : 'bg-white/5 text-slate-400 hover:bg-white/10'
            }`}
          >
            {m === 'text' ? '📝 Paste Text' : '📁 Upload File'}
          </button>
        ))}
      </div>

      {/* Input area */}
      <div className="glass-card p-6 mb-6">
        {mode === 'text' ? (
          <>
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-semibold text-slate-300">Raw Email Text</label>
              <button
                onClick={() => setEmailText(SAMPLE_EMAIL)}
                className="text-xs text-accent-blue hover:text-blue-400 transition-colors"
              >
                Load sample →
              </button>
            </div>
            <textarea
              id="email-input"
              className="input-field h-52 resize-none font-mono text-xs leading-relaxed"
              placeholder={"MV VESSEL NAME\nDWT 56000 / OPEN SINGAPORE / O/A 5TH JUNE\n---\n20,000 MT COAL\nLOAD PORT: NEWCASTLE\nDISCHARGE PORT: SHANGHAI\nLAYCAN: 15-25 JULY"}
              value={emailText}
              onChange={(e) => setEmailText(e.target.value)}
            />
            <div className="flex items-center justify-between mt-4">
              <span className="text-xs text-slate-500">
                {emailText.length} chars · {emailText.split('\n').length} lines
              </span>
              <div className="flex gap-3">
                <button
                  onClick={() => { setEmailText(''); setResults(null); setError(null); }}
                  className="btn-secondary text-xs px-3 py-1.5"
                >
                  Clear
                </button>
                <button
                  id="extract-btn"
                  onClick={handleExtract}
                  disabled={loading || !emailText.trim()}
                  className="btn-primary"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                      </svg>
                      Extracting…
                    </>
                  ) : (
                    <>⚡ Extract</>
                  )}
                </button>
              </div>
            </div>
          </>
        ) : (
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            className={`border-2 border-dashed rounded-xl p-10 text-center transition-all duration-300 cursor-pointer
              ${dragOver ? 'border-accent-blue bg-accent-blue/10' : 'border-white/10 hover:border-white/25 hover:bg-white/3'}`}
            onClick={() => document.getElementById('file-input').click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".txt,.pdf,.docx"
              className="hidden"
              onChange={(e) => handleFileUpload(e.target.files[0])}
            />
            <div className="text-4xl mb-3">
              {loading ? '⏳' : fileName ? '✅' : '📂'}
            </div>
            <p className="text-slate-300 font-medium mb-1">
              {fileName || 'Drop file here or click to browse'}
            </p>
            <p className="text-xs text-slate-500">.txt · .pdf · .docx</p>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="glass-card p-4 mb-6 border-l-4 border-l-red-500/60 animate-fade-in">
          <p className="text-sm text-red-400 flex items-start gap-2">
            <span>⚠</span> {error}
          </p>
        </div>
      )}

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-6 animate-slide-up">
          {[
            { label: 'Total Records', value: stats.total, color: 'text-white' },
            { label: 'Tonnage', value: stats.tonnage, color: 'text-tonnage' },
            { label: 'Cargo VC', value: stats.vc, color: 'text-cargovc' },
            { label: 'Cargo TC', value: stats.tc, color: 'text-cargotc' },
            { label: 'Warnings', value: stats.warnings, color: 'text-amber-400' },
          ].map(({ label, value, color }) => (
            <div key={label} className="glass-card p-4 text-center">
              <div className={`text-2xl font-bold ${color}`}>{value}</div>
              <div className="text-xs text-slate-500 mt-0.5">{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Results */}
      {results && results.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <h2 className="text-sm font-semibold text-slate-300">Extracted Records</h2>
            <div className="h-px flex-1 bg-white/5"></div>
          </div>
          {results.map((rec, i) => (
            <RecordCard key={i} record={rec} index={i} />
          ))}
        </div>
      )}

      {results && results.length === 0 && (
        <div className="glass-card p-10 text-center text-slate-500 animate-fade-in">
          <div className="text-4xl mb-3">🔍</div>
          <p>No records extracted. Try a different email.</p>
        </div>
      )}
    </div>
  );
}
