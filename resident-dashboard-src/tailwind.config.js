/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1e3a5f",
          light: "#2563eb",
        },
        accent: "#0ea5e9",
        "bg-base": "#f0f4f8",
      },
    },
  },
  plugins: [],
};
