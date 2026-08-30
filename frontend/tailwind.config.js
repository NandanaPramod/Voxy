/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "0",
      screens: { "2xl": "1152px" },
    },
    extend: {
      fontFamily: {
        display: ['"Space Grotesk"', "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      colors: {
        // Semantic tokens kept for compatibility
        border: "oklch(var(--border))",
        input: "oklch(var(--input))",
        ring: "oklch(var(--ring))",
        background: "oklch(var(--background))",
        foreground: "oklch(var(--foreground))",
        muted: { DEFAULT: "oklch(var(--muted))", foreground: "oklch(var(--muted-foreground))" },
        card: { DEFAULT: "oklch(var(--card))", foreground: "oklch(var(--card-foreground))" },
        popover: { DEFAULT: "oklch(var(--popover))", foreground: "oklch(var(--popover-foreground))" },
        primary: { DEFAULT: "oklch(var(--primary))", foreground: "oklch(var(--primary-foreground))" },
        secondary: { DEFAULT: "oklch(var(--secondary))", foreground: "oklch(var(--secondary-foreground))" },
        accent: { DEFAULT: "oklch(var(--accent))", foreground: "oklch(var(--accent-foreground))" },
        highlight: { DEFAULT: "oklch(var(--highlight))", foreground: "oklch(var(--highlight-foreground))" },
        destructive: { DEFAULT: "oklch(var(--destructive))", foreground: "oklch(var(--destructive-foreground))" },
        // Voxy forensic palette
        ink: "#1C201F",
        panel: "#252A29",
        panel2: "#303633",
        line: "#3E4644",
        brand: "#8BE8CB",
        brand2: "#9C7A97",
        steel: "#7EA2AA",
        lavender: "#888DA7",
        safe: "#8BE8CB",
        warn: "#C9A88E",
        danger: "#C97A93",
        critical: "#B55F7E",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      boxShadow: {
        glow: "0 0 40px -8px rgba(139, 232, 203, 0.45)",
        "glow-violet": "0 0 40px -8px rgba(156, 122, 151, 0.45)",
        card: "0 1px 0 0 rgba(255,255,255,0.03), 0 18px 40px -24px rgba(0,0,0,0.7)",
      },
      keyframes: {
        float: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-10px)" } },
        scan: { "0%": { transform: "translateY(-100%)" }, "100%": { transform: "translateY(900%)" } },
        shimmer: { "0%": { backgroundPosition: "-200% 0" }, "100%": { backgroundPosition: "200% 0" } },
        "pulse-ring": { "0%": { transform: "scale(0.9)", opacity: "0.7" }, "100%": { transform: "scale(1.5)", opacity: "0" } },
        wave: { "0%,100%": { transform: "scaleY(0.35)" }, "50%": { transform: "scaleY(1)" } },
      },
      animation: {
        float: "float 3s ease-in-out infinite",
        scan: "scan 2s linear infinite",
        shimmer: "shimmer 2.5s linear infinite",
        "pulse-ring": "pulse-ring 1.8s ease-out infinite",
        wave: "wave 1s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
