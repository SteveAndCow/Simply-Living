/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        black: '#000000',
        white: '#FFFFFF',
        gray: {
          500: '#888888',
          600: '#666666',
          700: '#444444',
        },
      },
      fontFamily: {
        body: ['Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'],
        display: ['Playfair Display', 'Georgia', 'serif'],
      },
      fontSize: {
        'hero': 'clamp(3.5rem, 10vw, 7.5rem)',
        'title': 'clamp(2rem, 5vw, 3.5rem)',
      },
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      transitionDuration: {
        '400': '400ms',
        '700': '700ms',
      },
    },
  },
  plugins: [],
}
