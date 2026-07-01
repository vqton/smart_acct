/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#1565C0',
          600: '#0d47a1',
          700: '#0a3d91',
          800: '#07347a',
          900: '#052b64',
        },
        success: { 400: '#4CAF50', 500: '#388E3C', 600: '#2E7D32' },
        warning: { 400: '#FF9800', 500: '#F57C00', 600: '#E65100' },
        danger: { 400: '#F44336', 500: '#D32F2F', 600: '#C62828' },
        surface: { 50: '#f8fafc', 100: '#f1f5f9', 200: '#e2e8f0' },
      },
      fontFamily: {
        sans: ['Tahoma', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['"Courier New"', 'monospace'],
      },
    },
  },
  plugins: [],
}
