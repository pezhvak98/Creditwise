/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bank-primary': '#1e40af',
        'bank-secondary': '#3b82f6',
        'bank-accent': '#10b981',
        'bank-danger': '#ef4444',
        'bank-warning': '#f59e0b',
      },
    },
    fontFamily: {
      sans: ['Vazirmatn', 'system-ui', 'sans-serif'],
      vazir: ['Vazirmatn', 'system-ui', 'sans-serif'],
    },
  },
  plugins: [],
}