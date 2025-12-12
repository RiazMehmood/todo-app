import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563eb', // blue-600
          hover: '#1d4ed8', // blue-700
        },
        success: {
          DEFAULT: '#16a34a', // green-600
          hover: '#15803d', // green-700
        },
        danger: {
          DEFAULT: '#dc2626', // red-600
          hover: '#b91c1c', // red-700
        },
      },
    },
  },
  plugins: [],
}
export default config
