module.exports = {
            content: ['./public/index.html', './public/assets/app.js'],
    darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brand: {
                            dark: '#07090e',
                            card: '#0f131c',
                            border: '#1b2234',
                            accent: '#00d2ff',
                            secondary: '#3a7bd5',
                            glow: 'rgba(0, 210, 255, 0.15)'
                        }
                    },
                    fontFamily: {
                        sans: ['Cairo', 'Plus Jakarta Sans', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace'],
                        en: ['Plus Jakarta Sans', 'Cairo', 'sans-serif']
                    }
                }
            }
        };
