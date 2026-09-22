/** @type {import('tailwindcss').Config} */
export default {
  // Paths to all source files that use Tailwind classes.
  // Tree-shaking removes unused styles in production builds.
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],

  theme: {
    extend: {
      // ── Custom color palette ────────────────────────────────────────────
      colors: {
        primary: {
          50:  '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        medical: {
          green:  '#10b981',
          red:    '#ef4444',
          amber:  '#f59e0b',
          blue:   '#3b82f6',
          purple: '#8b5cf6',
        },
      },

      // ── Typography ───────────────────────────────────────────────────────
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },

      // ── Spacing ──────────────────────────────────────────────────────────
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '112': '28rem',
        '128': '32rem',
      },

      // ── Border radius ─────────────────────────────────────────────────────
      borderRadius: {
        '4xl': '2rem',
      },

      // ── Box shadows ───────────────────────────────────────────────────────
      boxShadow: {
        'card': '0 2px 8px 0 rgba(0, 0, 0, 0.08)',
        'card-hover': '0 8px 24px 0 rgba(0, 0, 0, 0.12)',
      },
    },
  },

  plugins: [],
}
