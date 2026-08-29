/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bbdffd',
          300: '#7cc2fc',
          400: '#38a0f8',
          500: '#0e83e3',
          600: '#0265bc',
          700: '#035198',
          800: '#07457d',
          900: '#0c3a69',
          950: '#082545',
        },
      }
    },
  },
  plugins: [],
}
