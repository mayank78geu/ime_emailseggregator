/**
 * CategoryBadge — color-coded badge for TONNAGE / CARGO_VC / CARGO_TC
 */
export default function CategoryBadge({ category }) {
  const map = {
    TONNAGE: { label: 'TONNAGE', cls: 'badge-tonnage', icon: '⚓' },
    CARGO_VC: { label: 'CARGO VC', cls: 'badge-cargovc', icon: '🚢' },
    CARGO_TC: { label: 'CARGO TC', cls: 'badge-cargotc', icon: '📋' },
  };
  const item = map[category] || { label: category, cls: 'badge-tonnage', icon: '📦' };
  return (
    <span className={item.cls}>
      {item.icon} {item.label}
    </span>
  );
}
