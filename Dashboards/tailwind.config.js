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
  themes: [
    {
      forestdash: {
        "primary": "#2E6F4E",
        "secondary": "#5DAA73",
        "accent": "#B2D2FB",
        "neutral": "#244732",
        "base-100": "#2F5C42",
        "base-200": "#2A543B",
        "base-300": "#254D35",
        "info": "#7BC6C8",
        "success": "#68D391",
        "warning": "#F6C945",
        "error": "#F87171",
        "hehe": "#FFF"
      }
    },
    "forest" // fallback
  ]
}
}
