/**
 * Navbar — sticky navigation bar with links to all pages
 */
import { NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'Extract', icon: '⚡' },
  { to: '/records', label: 'Records', icon: '📊' },
  { to: '/search', label: 'Search', icon: '🔍' },
];

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 bg-navy-900/90 backdrop-blur-xl border-b border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-blue-500/25">
            ⚓
          </div>
          <div>
            <span className="text-white font-bold text-sm tracking-tight">ShipMail</span>
            <span className="text-accent-blue font-bold text-sm"> Extractor</span>
          </div>
        </div>

        {/* Nav links */}
        <div className="flex items-center gap-1">
          {links.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-accent-blue/15 text-accent-blue border border-accent-blue/25'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`
              }
            >
              <span>{icon}</span>
              <span className="hidden sm:inline">{label}</span>
            </NavLink>
          ))}
        </div>

        {/* Status dot */}
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-slow"></span>
          <span className="hidden sm:inline">API Live</span>
        </div>
      </div>
    </nav>
  );
}
