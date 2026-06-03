/**
 * RecordCard — renders one extracted shipping record as a premium card
 */
import CategoryBadge from './CategoryBadge';

const Field = ({ label, value }) => (
  <div className="field-row">
    <span className="field-label">{label}</span>
    {value ? (
      <span className="field-value">{value}</span>
    ) : (
      <span className="field-null">—</span>
    )}
  </div>
);

const borderMap = {
  TONNAGE: 'border-l-tonnage/60',
  CARGO_VC: 'border-l-cargovc/60',
  CARGO_TC: 'border-l-cargotc/60',
};

const glowMap = {
  TONNAGE: 'hover:shadow-blue-500/10',
  CARGO_VC: 'hover:shadow-emerald-500/10',
  CARGO_TC: 'hover:shadow-amber-500/10',
};

export default function RecordCard({ record, index }) {
  const { category, _warnings = [], confidence_score, confidence_level, ...fields } = record;
  const borderClass = borderMap[category] || 'border-l-white/20';
  const glowClass = glowMap[category] || '';

  const renderFields = () => {
    if (category === 'TONNAGE') {
      return (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <Field label="Vessel Name" value={fields.vessel_name} />
          <Field label="DWT" value={fields.vessel_size_dwt} />
          <Field label="Open Port" value={fields.open_port} />
          <Field label="Open Date" value={fields.open_date} />
          <Field label="Flag" value={fields.flag} />
          <Field label="Built Year" value={fields.built_year} />
          {fields.account_name && <Field label="Account" value={fields.account_name} />}
          {fields.vessel_type && <Field label="Type" value={fields.vessel_type} />}
        </div>
      );
    }
    if (category === 'CARGO_VC') {
      return (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <Field label="Cargo" value={fields.cargo_name} />
          <Field label="Quantity" value={fields.quantity} />
          <Field label="Loading Port" value={fields.loading_port} />
          <Field label="Discharge Port" value={fields.discharge_port} />
          <Field label="Laycan" value={fields.laycan_raw} />
          <Field label="Commission" value={fields.commission} />
          {fields.account_name && <Field label="Account" value={fields.account_name} />}
        </div>
      );
    }
    if (category === 'CARGO_TC') {
      return (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <Field label="Delivery Port" value={fields.delivery_port} />
          <Field label="Redelivery Port" value={fields.redelivery_port} />
          <Field label="Duration" value={fields.duration} />
          <Field label="Laycan" value={fields.laycan_raw} />
          <Field label="Vessel Size" value={fields.vessel_size} />
          <Field label="Commission" value={fields.commission} />
          {fields.cargo_name && <Field label="Cargo" value={fields.cargo_name} />}
          {fields.account_name && <Field label="Account" value={fields.account_name} />}
        </div>
      );
    }
    // Unknown category fallback
    return (
      <pre className="text-xs text-slate-400 font-mono overflow-auto max-h-40">
        {JSON.stringify(fields, null, 2)}
      </pre>
    );
  };

  return (
    <div
      className={`glass-card border-l-4 ${borderClass} p-5 animate-slide-up transition-all duration-300 hover:shadow-xl ${glowClass}`}
      style={{ animationDelay: `${index * 60}ms` }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <CategoryBadge category={category} />
          <span className="text-xs text-slate-500 font-mono">Record #{index + 1}</span>
          {confidence_score !== undefined && (
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold font-mono tracking-wider uppercase border
                ${confidence_level === 'HIGH' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25' : 
                  confidence_level === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border-amber-500/25' : 
                  'bg-red-500/10 text-red-400 border-red-500/25'}`}
            >
              🛡️ {confidence_score}% {confidence_level}
            </span>
          )}
        </div>
        {_warnings.length > 0 && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/25">
            ⚠ {_warnings.length} warning{_warnings.length > 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Fields */}
      {renderFields()}

      {/* Warnings */}
      {_warnings.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/5">
          <p className="text-xs font-semibold text-amber-400 mb-2">Validation Warnings</p>
          <ul className="space-y-1">
            {_warnings.map((w, i) => (
              <li key={i} className="text-xs text-amber-300/70 flex items-start gap-1.5">
                <span className="mt-0.5">›</span> {w}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
