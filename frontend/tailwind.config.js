module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/flowbite-react/**/*.js"
  ],
  theme: {
  extend: {
    colors: {
      primary: "#2563eb", // blue-ish
      secondary: "#10b981", // green
      danger: "#ef4444",
    },
    fontFamily: {
      sans: ['Inter', 'sans-serif'],
    },
  },
  },
  plugins: [
    require('flowbite/plugin')
  ],
}
