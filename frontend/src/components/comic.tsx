import { motion, type HTMLMotionProps } from "framer-motion";
import type { ReactNode } from "react";
import { useUI } from "../store";

type Variant = "red" | "cyan" | "yellow" | "ghost";
const VARIANT: Record<Variant, string> = {
  red: "bg-spidey text-white",
  cyan: "bg-electric text-miles",
  yellow: "bg-comic text-miles",
  ghost: "bg-white text-miles dark:bg-navy dark:text-paper",
};
const SIZE = { sm: "px-3 py-1.5 text-base", md: "px-5 py-2.5 text-xl", lg: "px-7 py-3 text-2xl" };
const BTN = "inline-flex items-center justify-center gap-2 font-display tracking-wider border-[3px] border-black shadow-comic-sm rounded-md select-none disabled:opacity-50 disabled:cursor-not-allowed";

type Extra = { variant?: Variant; size?: keyof typeof SIZE };

export function ComicButton({ variant = "red", size = "md", className = "", ...rest }: HTMLMotionProps<"button"> & Extra) {
  return (
    <motion.button whileTap={{ scale: 0.92, y: 2 }} whileHover={{ y: -2 }}
      className={`${BTN} ${VARIANT[variant]} ${SIZE[size]} ${className}`} {...rest} />
  );
}

export function ComicLink({ variant = "red", size = "md", className = "", ...rest }: HTMLMotionProps<"a"> & Extra) {
  return (
    <motion.a whileTap={{ scale: 0.92, y: 2 }} whileHover={{ y: -2 }}
      className={`${BTN} ${VARIANT[variant]} ${SIZE[size]} ${className}`} {...rest} />
  );
}

export function ComicPanel({ children, caption, className = "" }: { children: ReactNode; caption?: string; className?: string }) {
  return (
    <div className={`panel relative p-5 ${className}`}>
      {caption && <span className="caption absolute -top-4 left-4 text-sm">{caption}</span>}
      {children}
    </div>
  );
}

export function StarBurst({ children, size = 64, color = "#FFD60A", spikes = 14, className = "" }:
  { children?: ReactNode; size?: number; color?: string; spikes?: number; className?: string }) {
  const pts = Array.from({ length: spikes * 2 }, (_, i) => {
    const r = i % 2 === 0 ? 49 : 37;
    const a = (Math.PI * i) / spikes;
    return `${50 + r * Math.cos(a)},${50 + r * Math.sin(a)}`;
  }).join(" ");
  return (
    <div className={`relative inline-grid place-items-center animate-pow ${className}`} style={{ width: size, height: size }}>
      <svg viewBox="0 0 100 100" className="absolute inset-0" aria-hidden="true">
        <polygon points={pts} fill={color} stroke="#000" strokeWidth="4" strokeLinejoin="round" />
      </svg>
      <span className="relative font-display text-miles leading-none text-center" style={{ fontSize: size / 3.6 }}>{children}</span>
    </div>
  );
}

export function HalftoneBg({ className = "", animated = false }: { className?: string; animated?: boolean }) {
  return <div aria-hidden="true" className={`pointer-events-none absolute inset-0 halftone ${animated ? "animate-halftone-pan" : ""} ${className}`} />;
}

export function SpeechBubble({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`relative inline-block max-w-2xl rounded-3xl border-[3px] border-black bg-paper text-miles px-5 py-3 shadow-comic-sm ${className}`}>
      <p className="font-semibold">{children}</p>
      <svg className="absolute -bottom-[18px] left-10" width="30" height="20" viewBox="0 0 30 20" aria-hidden="true">
        <path d="M0 0 L30 0 L6 20 Z" fill="#F7F3E8" stroke="#000" strokeWidth="3" />
        <path d="M2 0 L28 0" stroke="#F7F3E8" strokeWidth="4" />
      </svg>
    </div>
  );
}

export function ThemeToggle() {
  const theme = useUI((s) => s.theme);
  const toggle = useUI((s) => s.toggleTheme);
  const dark = theme === "dark";
  return (
    <button onClick={toggle} aria-label={`Switch to ${dark ? "light comic paper" : "dark"} mode`} aria-pressed={!dark}
      className="shrink-0 w-11 h-11 grid place-items-center rounded-full border-[3px] border-black bg-comic text-miles shadow-comic-sm text-lg">
      <span aria-hidden="true">{dark ? "☀" : "☾"}</span>
    </button>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div className={`panel relative overflow-hidden ${className}`} aria-hidden="true">
      <HalftoneBg animated />
      <div className="absolute inset-0 animate-pulse bg-black/5 dark:bg-white/5" />
    </div>
  );
}

function ring(r: number) {
  return Array.from({ length: 8 }, (_, i) => {
    const a = (Math.PI / 4) * i;
    return `${24 + r * Math.sin(a)},${24 - r * Math.cos(a)}`;
  }).join(" ");
}

export function WebLogo({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 48 48" className={className} aria-hidden="true">
      <circle cx="24" cy="24" r="22" fill="#0B0B12" stroke="#E23636" strokeWidth="3" />
      <g stroke="#F7F3E8" strokeWidth="1.4" fill="none">
        {[0, 45, 90, 135].map((a) => <line key={a} x1="24" y1="3" x2="24" y2="45" transform={`rotate(${a} 24 24)`} />)}
        <polygon points={ring(16)} />
        <polygon points={ring(9)} />
      </g>
    </svg>
  );
}

export function SectionTitle({ kicker, title, id }: { kicker?: string; title: string; id?: string }) {
  return (
    <div className="mb-6">
      {kicker && <span className="caption text-sm">{kicker}</span>}
      <h2 id={id} className="headline mt-3 text-4xl sm:text-5xl">{title}</h2>
    </div>
  );
}
export const ZigZag = () => <div className="zigzag" aria-hidden="true" />;