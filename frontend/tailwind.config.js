/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Figtree', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Operations console chrome
        ink: {
          900: '#0B1623',
          800: '#132234',
          700: '#1C3047',
          600: '#2A4460',
          300: '#8FA3B8',
        },
        paper: '#F6F7F9',
        line: '#E3E7ED',
        // Signal colours, one meaning each
        cancelled: '#B42318',
        delayed: '#B54708',
        onTime: '#067647',
        authorized: '#0E7C66',
        escalate: '#6B3FA0',
        seal: '#0B6B6B',
      },
      boxShadow: {
        card: '0 1px 2px rgba(11, 22, 35, 0.05)',
        lift: '0 8px 24px rgba(11, 22, 35, 0.08)',
      },
      keyframes: {
        rise: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        rise: 'rise 180ms ease-out',
      },
    },
  },
  plugins: [],
}