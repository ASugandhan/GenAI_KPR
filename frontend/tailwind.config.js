/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './app/**/*.{js,ts,jsx,tsx,mdx}',
        './components/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                cyber: {
                    bg: '#0a0e1a',
                    card: '#111827',
                    border: '#1e293b',
                    accent: '#00f0ff',
                    green: '#00ff88',
                    red: '#ff3366',
                    yellow: '#ffcc00',
                    purple: '#a855f7',
                    blue: '#3b82f6',
                },
            },
            fontFamily: {
                mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            animation: {
                'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
                'slide-in': 'slide-in 0.3s ease-out',
                'fade-in': 'fade-in 0.5s ease-out',
                'scan-line': 'scan-line 3s linear infinite',
            },
            keyframes: {
                'pulse-glow': {
                    '0%, 100%': { boxShadow: '0 0 5px rgba(0, 240, 255, 0.3)' },
                    '50%': { boxShadow: '0 0 20px rgba(0, 240, 255, 0.6)' },
                },
                'slide-in': {
                    from: { transform: 'translateX(-10px)', opacity: '0' },
                    to: { transform: 'translateX(0)', opacity: '1' },
                },
                'fade-in': {
                    from: { opacity: '0' },
                    to: { opacity: '1' },
                },
                'scan-line': {
                    '0%': { transform: 'translateY(-100%)' },
                    '100%': { transform: 'translateY(100%)' },
                },
            },
        },
    },
    plugins: [],
};
