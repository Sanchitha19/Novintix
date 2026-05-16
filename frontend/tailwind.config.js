/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: "#0F1117",
          panel: "#161B22",
          border: "#30363D",
        },
        brand: {
          blue: "#3B82F6",
          amber: "#F59E0B",
          red: "#EF4444",
          purple: "#8B5CF6",
          green: "#10B981",
        }
      },
      fontFamily: {
        sans: ['"DM Sans"', 'sans-serif'],
        mono: ['"Space Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
