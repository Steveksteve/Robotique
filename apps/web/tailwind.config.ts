import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains)', 'monospace'],
      },
      colors: {
        background: '#0f0f11', // Slightly lighter, warmer dark (like Linear/macOS)
        surface: '#18181b',
        'surface-highlight': '#27272a',
        border: 'rgba(255, 255, 255, 0.06)',
        'border-highlight': 'rgba(255, 255, 255, 0.1)',
        primary: '#007AFF', // Apple-style bright blue
        'primary-glow': 'rgba(0, 122, 255, 0.4)',
        success: '#34C759', // Apple Green
        warning: '#FF9500', // Apple Orange
        danger: '#FF3B30', // Apple Red
        text: {
          primary: '#F5F5F7', // Apple white-ish
          secondary: '#86868b', // Apple gray
          tertiary: '#424245',
        }
      },
      boxShadow: {
        'glow': '0 0 20px rgba(59, 130, 246, 0.15)',
        'glow-success': '0 0 20px rgba(16, 185, 129, 0.15)',
        'glow-danger': '0 0 20px rgba(239, 68, 68, 0.2)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
      backdropBlur: {
        'xs': '2px',
      }
    },
  },
  plugins: [],
}
export default config
