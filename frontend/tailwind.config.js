/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        navy: {
          900: '#0a0f1e',
          800: '#0d1526',
          700: '#111b33',
          600: '#1a2744',
          500: '#243358',
        },
        accent: {
          blue: '#3b82f6',
          cyan: '#06b6d4',
          purple: '#8b5cf6',
        },
        tonnage: {
          DEFAULT: '#3b82f6',
          light: '#93c5fd',
          dark: '#1d4ed8',
          bg: 'rgba(59,130,246,0.12)',
        },
        cargovc: {
          DEFAULT: '#10b981',
          light: '#6ee7b7',
          dark: '#047857',
          bg: 'rgba(16,185,129,0.12)',
        },
        cargotc: {
          DEFAULT: '#f59e0b',
          light: '#fcd34d',
          dark: '#b45309',
          bg: 'rgba(245,158,11,0.12)',
        },
      },
      backgroundImage: {
        'grid-pattern': "linear-gradient(rgba(59,130,246,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(59,130,246,0.05) 1px, transparent 1px)",
      },
      backgroundSize: {
        'grid': '32px 32px',
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
