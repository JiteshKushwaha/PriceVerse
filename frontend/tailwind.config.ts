import type { Config } from "tailwindcss";

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        miles: "#0B0B12", navy: "#101428", spidey: "#E23636", magenta: "#FF2E93",
        electric: "#00E5FF", venom: "#7B2FF7", comic: "#FFD60A", paper: "#F7F3E8",
      },
      fontFamily: {
        display: ["Bangers", "Impact", "sans-serif"],
        caption: ['"Barlow Condensed"', "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        mono: ['"Space Mono"', "monospace"],
      },
      boxShadow: { comic: "6px 6px 0 #000", "comic-sm": "3px 3px 0 #000" },
      keyframes: {
        pow: { "0%": { transform: "scale(0) rotate(-12deg)", opacity: "0" }, "70%": { transform: "scale(1.15) rotate(3deg)", opacity: "1" }, "100%": { transform: "scale(1) rotate(0)" } },
        glitch: { "0%,100%": { textShadow: "3px 3px 0 #00E5FF, -3px -3px 0 #FF2E93" }, "33%": { textShadow: "-3px 2px 0 #00E5FF, 3px -2px 0 #FF2E93" }, "66%": { textShadow: "2px -3px 0 #00E5FF, -2px 3px 0 #FF2E93" } },
        swing: { "0%,100%": { transform: "rotate(-4deg)" }, "50%": { transform: "rotate(4deg)" } },
        "halftone-pan": { "0%": { backgroundPosition: "0 0" }, "100%": { backgroundPosition: "40px 40px" } },
      },
      animation: {
        pow: "pow .45s ease-out both", glitch: "glitch .35s steps(2) infinite",
        swing: "swing 2.4s ease-in-out infinite", "halftone-pan": "halftone-pan 6s linear infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;