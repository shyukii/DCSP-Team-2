/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}"
  ],
  theme: { extend: {} },
  plugins: [require('daisyui')],
  // (optional) DaisyUI themes:
  daisyui: {
    themes: ["light", "dark", "forest"]
  }
}
