/**
 * SearchPage — filter form for all three record types + live results
 */
import { useState } from 'react';
import { searchTonnage, searchCargoVC, searchCargoTC } from '../api/shippingApi';
import CategoryBadge from '../components/CategoryBadge';

const TABS = [
  { id: 'tonnage', label: 'Tonnage', icon: '⚓', badge: 'badge-tonnage' },
  { id: 'cargo_vc', label: 'Cargo VC', icon: '🚢', badge: 'badge-cargovc' },
  { id: 'cargo_tc', label: 'Cargo TC', icon: '📋', badge: 'badge-cargotc' },
];

function InputField({ id, label, placeholder, value, onChange }) {
  return (
    <div>
      <label htmlFor={id} className="block text-xs font-medium text-slate-400 mb-1.5">
        {label}
      </label>
      <input
        id={id}
        type="text"
        className="input-field"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

function NumberField({ id, label, placeholder, value, onChange }) {
  return (
    <div>
      <label htmlFor={id} className="block text-xs font-medium text-slate-400 mb-1.5">
        {label}
      </label>
      <input
        id={id}
        type="number"
        className="input-field"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

// ── Tonnage results table
function TonnageTable({ data }) {
  if (!data.length) return <EmptyState />;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/5">
            {['Vessel Name', 'DWT', 'Open Port', 'Open Date', 'Flag', 'Built'].map((h) => (
              <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((r, i) => (
            <tr key={r.id} className="border-b border-white/3 hover:bg-white/3 transition-colors animate-fade-in" style={{ animationDelay: `${i * 30}ms` }}>
              <td className="px-4 py-3 font-medium text-slate-200">{r.vessel_name || '—'}</td>
              <td className="px-4 py-3 font-mono text-accent-blue">{r.vessel_size_dwt || '—'}</td>
              <td className="px-4 py-3 text-slate-300">{r.open_port || '—'}</td>
              <td className="px-4 py-3 text-slate-400 text-xs">{r.open_date || '—'}</td>
              <td className="px-4 py-3 text-slate-400 text-xs">{r.flag || '—'}</td>
              <td className="px-4 py-3 text-slate-400 text-xs">{r.built_year || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Cargo VC results table
function CargoVCTable({ data }) {
  if (!data.length) return <EmptyState />;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/5">
            {['Cargo', 'Quantity', 'Loading Port', 'Discharge Port', 'Laycan', 'Commission'].map((h) => (
              <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((r, i) => (
            <tr key={r.id} className="border-b border-white/3 hover:bg-white/3 transition-colors animate-fade-in" style={{ animationDelay: `${i * 30}ms` }}>
              <td className="px-4 py-3 font-medium text-slate-200">{r.cargo_name || '—'}</td>
              <td className="px-4 py-3 font-mono text-cargovc">{r.quantity || '—'}</td>
              <td className="px-4 py-3 text-slate-300">{r.loading_port || '—'}</td>
              <td className="px-4 py-3 text-slate-300">{r.discharge_port || '—'}</td>
              <td className="px-4 py-3 text-slate-400 text-xs">{r.laycan_raw || '—'}</td>
              <td className="px-4 py-3 text-slate-400 text-xs">{r.commission || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Cargo TC results table
function CargoTCTable({ data }) {
  if (!data.length) return <EmptyState />;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/5">
            {['Delivery Port', 'Redelivery Port', 'Duration', 'Laycan', 'Vessel Size', 'Commission'].map((h) => (
              <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((r, i) => (
            <tr key={r.id} className="border-b border-white/3 hover:bg-white/3 transition-colors animate-fade-in" style={{ animationDelay: `${i * 30}ms` }}>
              <td className="px-4 py-3 font-medium text-slate-200">{r.delivery_port || '—'}</td>
              <td className="px-4 py-3 text-slate-300">{r.redelivery_port || '—'}</td>
              <td className="px-4 py-3 font-mono text-cargotc">{r.duration || '—'}</td>
              <td className="px-4 py-3 text-slate-400 text-xs">{r.laycan_raw || '—'}</td>
              <td className="px-4 py-3 text-slate-400 text-xs">{r.vessel_size || '—'}</td>
              <td className="px-4 py-3 text-slate-400 text-xs">{r.commission || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="py-16 text-center text-slate-500">
      <div className="text-4xl mb-3">🔍</div>
      <p>No results found. Try different filters.</p>
    </div>
  );
}

export default function SearchPage() {
  const [activeTab, setActiveTab] = useState('tonnage');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState(null);

  // Tonnage filters
  const [tPort, setTPort] = useState('');
  const [tMinDwt, setTMinDwt] = useState('');
  const [tMaxDwt, setTMaxDwt] = useState('');
  const [tFlag, setTFlag] = useState('');
  const [tYear, setTYear] = useState('');

  // Cargo VC filters
  const [vcLoad, setVcLoad] = useState('');
  const [vcDisch, setVcDisch] = useState('');
  const [vcLaycan, setVcLaycan] = useState('');

  // Cargo TC filters
  const [tcDely, setTcDely] = useState('');
  const [tcRedel, setTcRedel] = useState('');
  const [tcSize, setTcSize] = useState('');

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      let res;
      if (activeTab === 'tonnage') {
        const params = {};
        if (tPort) params.open_port = tPort;
        if (tMinDwt) params.min_dwt = parseInt(tMinDwt);
        if (tMaxDwt) params.max_dwt = parseInt(tMaxDwt);
        if (tFlag) params.flag = tFlag;
        if (tYear) params.built_year = tYear;
        res = await searchTonnage(params);
      } else if (activeTab === 'cargo_vc') {
        const params = {};
        if (vcLoad) params.loading_port = vcLoad;
        if (vcDisch) params.discharge_port = vcDisch;
        if (vcLaycan) params.laycan_month = vcLaycan;
        res = await searchCargoVC(params);
      } else {
        const params = {};
        if (tcDely) params.delivery_port = tcDely;
        if (tcRedel) params.redelivery_port = tcRedel;
        if (tcSize) params.vessel_size = tcSize;
        res = await searchCargoTC(params);
      }
      setResults(res.data || []);
      setTotal(res.total || 0);
    } catch (e) {
      setError('Search failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setTPort(''); setTMinDwt(''); setTMaxDwt(''); setTFlag(''); setTYear('');
    setVcLoad(''); setVcDisch(''); setVcLaycan('');
    setTcDely(''); setTcRedel(''); setTcSize('');
    setResults(null); setError(null);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10 animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Search <span className="text-gradient">Records</span>
        </h1>
        <p className="text-slate-400 text-sm">Filter extracted records by port, DWT, laycan, and more.</p>
      </div>

      {/* Category tabs */}
      <div className="flex gap-2 mb-5 flex-wrap">
        {TABS.map(({ id, label, icon }) => (
          <button
            key={id}
            onClick={() => { setActiveTab(id); setResults(null); setError(null); }}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
              activeTab === id
                ? id === 'tonnage'
                  ? 'bg-tonnage-bg text-tonnage border border-tonnage/30'
                  : id === 'cargo_vc'
                  ? 'bg-cargovc-bg text-cargovc border border-cargovc/30'
                  : 'bg-cargotc-bg text-cargotc border border-cargotc/30'
                : 'bg-white/5 text-slate-400 hover:bg-white/10 border border-transparent'
            }`}
          >
            {icon} {label}
          </button>
        ))}
      </div>

      {/* Filter form */}
      <div className="glass-card p-6 mb-6">
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mb-5">
          {activeTab === 'tonnage' && (
            <>
              <InputField id="t-port" label="Open Port" placeholder="e.g. SINGAPORE" value={tPort} onChange={setTPort} />
              <NumberField id="t-min-dwt" label="Min DWT" placeholder="e.g. 30000" value={tMinDwt} onChange={setTMinDwt} />
              <NumberField id="t-max-dwt" label="Max DWT" placeholder="e.g. 80000" value={tMaxDwt} onChange={setTMaxDwt} />
              <InputField id="t-flag" label="Flag" placeholder="e.g. PANAMA" value={tFlag} onChange={setTFlag} />
              <InputField id="t-year" label="Built Year" placeholder="e.g. 2015" value={tYear} onChange={setTYear} />
            </>
          )}
          {activeTab === 'cargo_vc' && (
            <>
              <InputField id="vc-load" label="Loading Port" placeholder="e.g. JEDDAH" value={vcLoad} onChange={setVcLoad} />
              <InputField id="vc-disch" label="Discharge Port" placeholder="e.g. BILBAO" value={vcDisch} onChange={setVcDisch} />
              <InputField id="vc-laycan" label="Laycan Month" placeholder="e.g. JUNE" value={vcLaycan} onChange={setVcLaycan} />
            </>
          )}
          {activeTab === 'cargo_tc' && (
            <>
              <InputField id="tc-dely" label="Delivery Port" placeholder="e.g. VANCOUVER" value={tcDely} onChange={setTcDely} />
              <InputField id="tc-redel" label="Redelivery Port" placeholder="e.g. MED" value={tcRedel} onChange={setTcRedel} />
              <InputField id="tc-size" label="Vessel Size" placeholder="e.g. SUPRAMAX" value={tcSize} onChange={setTcSize} />
            </>
          )}
        </div>

        <div className="flex items-center gap-3">
          <button
            id="search-btn"
            onClick={handleSearch}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Searching…
              </>
            ) : (
              <>🔍 Search</>
            )}
          </button>
          <button onClick={handleReset} className="btn-secondary">
            ✕ Reset
          </button>
          {results !== null && (
            <span className="text-sm text-slate-400 ml-auto">
              <span className="font-semibold text-white">{total}</span> result{total !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="glass-card p-4 mb-6 border-l-4 border-l-red-500/60">
          <p className="text-sm text-red-400">⚠ {error}</p>
        </div>
      )}

      {/* Results table */}
      {results !== null && (
        <div className="glass-card overflow-hidden animate-slide-up">
          {activeTab === 'tonnage' && <TonnageTable data={results} />}
          {activeTab === 'cargo_vc' && <CargoVCTable data={results} />}
          {activeTab === 'cargo_tc' && <CargoTCTable data={results} />}
        </div>
      )}
    </div>
  );
}
