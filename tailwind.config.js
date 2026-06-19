/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        police: {
          950: '#020617', # slate-950
          900: '#0f172a', # slate-900
          800: '#1e293b', # slate-800
          700: '#334155', # slate-700
          blue: '#1d4ed8', # blue-700
          accent: '#06b6d4', # cyan-500
          glow: '#6366f1'  # indigo-500
        }
      }
    },
  },
  plugins: [],
}
