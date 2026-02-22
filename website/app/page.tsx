"use client";

import { FC, useRef, useEffect, useState } from "react";
import { motion, useMotionValue, useSpring, useTransform, useScroll, useInView } from "framer-motion";

// ============================================================================
// CUSTOM CURSOR
// ============================================================================

const CustomCursor: FC = () => {
  const cursorX = useMotionValue(-100);
  const cursorY = useMotionValue(-100);
  const dotX = useMotionValue(-100);
  const dotY = useMotionValue(-100);

  const springConfig = { damping: 25, stiffness: 200 };
  const cursorXSpring = useSpring(cursorX, springConfig);
  const cursorYSpring = useSpring(cursorY, springConfig);

  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    const moveCursor = (e: MouseEvent) => {
      cursorX.set(e.clientX);
      cursorY.set(e.clientY);
      dotX.set(e.clientX);
      dotY.set(e.clientY);
    };

    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.matches('a, button, [data-cursor-hover]')) {
        setIsHovering(true);
      }
    };

    const handleMouseOut = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.matches('a, button, [data-cursor-hover]')) {
        setIsHovering(false);
      }
    };

    window.addEventListener("mousemove", moveCursor);
    document.addEventListener("mouseover", handleMouseOver);
    document.addEventListener("mouseout", handleMouseOut);

    return () => {
      window.removeEventListener("mousemove", moveCursor);
      document.removeEventListener("mouseover", handleMouseOver);
      document.removeEventListener("mouseout", handleMouseOut);
    };
  }, [cursorX, cursorY, dotX, dotY]);

  return (
    <>
      <motion.div
        className={`cursor ${isHovering ? 'hover' : ''}`}
        style={{ left: cursorXSpring, top: cursorYSpring }}
      />
      <motion.div
        className="cursor-dot"
        style={{ left: dotX, top: dotY }}
      />
    </>
  );
};

// ============================================================================
// FLOATING PARTICLES
// ============================================================================

const Particles: FC = () => {
  const [particles, setParticles] = useState<Array<{ id: number; x: number; y: number; delay: number }>>([]);

  useEffect(() => {
    const newParticles = Array.from({ length: 30 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 5,
    }));
    setParticles(newParticles);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="particle"
          initial={{ opacity: 0 }}
          animate={{
            opacity: [0.2, 0.5, 0.2],
            scale: [1, 1.5, 1],
            x: [0, Math.random() * 100 - 50, 0],
            y: [0, Math.random() * 100 - 50, 0],
          }}
          transition={{
            duration: 10 + Math.random() * 10,
            repeat: Infinity,
            delay: p.delay,
            ease: "easeInOut",
          }}
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
          }}
        />
      ))}
    </div>
  );
};

// ============================================================================
// MOUSE PARALLAX WRAPPER
// ============================================================================

const MouseParallax: FC<{
  children: React.ReactNode;
  intensity?: number;
  className?: string;
}> = ({ children, intensity = 0.05, className = "" }) => {
  const ref = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const springConfig = { damping: 50, stiffness: 100 };
  const xSpring = useSpring(x, springConfig);
  const ySpring = useSpring(y, springConfig);

  useEffect(() => {
    const handleMouse = (e: MouseEvent) => {
      const rect = ref.current?.getBoundingClientRect();
      if (!rect) return;
      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;
      x.set((e.clientX - centerX) * intensity);
      y.set((e.clientY - centerY) * intensity);
    };

    window.addEventListener("mousemove", handleMouse);
    return () => window.removeEventListener("mousemove", handleMouse);
  }, [intensity, x, y]);

  return (
    <motion.div ref={ref} style={{ x: xSpring, y: ySpring }} className={className}>
      {children}
    </motion.div>
  );
};

// ============================================================================
// ANIMATED TEXT REVEAL
// ============================================================================

const TextReveal: FC<{
  children: string;
  className?: string;
  delay?: number;
}> = ({ children, className = "", delay = 0 }) => {
  return (
    <span className={`headline-word ${className}`}>
      <motion.span
        initial={{ y: "110%" }}
        animate={{ y: "0%" }}
        transition={{
          duration: 1.2,
          delay,
          ease: [0.16, 1, 0.3, 1],
        }}
      >
        {children}
      </motion.span>
    </span>
  );
};

// ============================================================================
// MAGNETIC BUTTON
// ============================================================================

const MagneticButton: FC<{
  children: React.ReactNode;
  href: string;
  variant?: "primary" | "secondary";
  className?: string;
}> = ({ children, href, variant = "primary", className = "" }) => {
  const ref = useRef<HTMLAnchorElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const springConfig = { damping: 15, stiffness: 150 };
  const xSpring = useSpring(x, springConfig);
  const ySpring = useSpring(y, springConfig);

  const handleMouse = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    x.set((e.clientX - centerX) * 0.3);
    y.set((e.clientY - centerY) * 0.3);
  };

  const reset = () => {
    x.set(0);
    y.set(0);
  };

  if (variant === "secondary") {
    return (
      <motion.a
        ref={ref}
        href={href}
        style={{ x: xSpring, y: ySpring }}
        onMouseMove={handleMouse}
        onMouseLeave={reset}
        className={`group relative inline-flex items-center gap-3 px-6 py-4 text-sm font-medium text-white/60 hover:text-white transition-colors ${className}`}
        data-cursor-hover
      >
        <span className="relative z-10 flex items-center gap-3">{children}</span>
        <span className="absolute bottom-3 left-6 right-6 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent scale-x-0 group-hover:scale-x-100 transition-transform duration-500" />
      </motion.a>
    );
  }

  return (
    <motion.a
      ref={ref}
      href={href}
      target={href.startsWith("http") ? "_blank" : undefined}
      rel={href.startsWith("http") ? "noreferrer" : undefined}
      style={{ x: xSpring, y: ySpring }}
      onMouseMove={handleMouse}
      onMouseLeave={reset}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`magnetic-btn group relative inline-flex items-center gap-4 overflow-hidden ${className}`}
      data-cursor-hover
    >
      {/* Animated background layers */}
      <span className="absolute inset-0 bg-white rounded-full" />
      <span className="absolute inset-0 bg-gradient-to-r from-cyan-400 via-violet-400 to-fuchsia-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      {/* Shine effect */}
      <span className="absolute inset-0 opacity-0 group-hover:opacity-100">
        <span className="absolute inset-0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700 bg-gradient-to-r from-transparent via-white/30 to-transparent skew-x-12" />
      </span>

      {/* Content */}
      <span className="relative z-10 flex items-center gap-3 px-8 py-5 text-sm font-semibold tracking-wide uppercase text-black group-hover:text-white transition-colors duration-300">
        {children}
      </span>

      {/* Border glow */}
      <span className="absolute -inset-px rounded-full bg-gradient-to-r from-cyan-400 via-violet-400 to-fuchsia-400 opacity-0 group-hover:opacity-50 blur-sm transition-opacity duration-500" />
    </motion.a>
  );
};

// ============================================================================
// ANIMATED TERMINAL - REAL PRODUCT DEMO
// ============================================================================

const AnimatedTerminal: FC<{
  lines: Array<{ type: 'command' | 'output' | 'comment' | 'success' | 'file'; content: string; delay?: number }>;
  title?: string;
  className?: string;
}> = ({ lines, title = "terminal", className = "" }) => {
  const [visibleLines, setVisibleLines] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (!isInView) return;

    let timeout: NodeJS.Timeout;
    const showNextLine = (index: number) => {
      if (index < lines.length) {
        const delay = lines[index].delay || 400;
        timeout = setTimeout(() => {
          setVisibleLines(index + 1);
          showNextLine(index + 1);
        }, delay);
      }
    };

    showNextLine(0);
    return () => clearTimeout(timeout);
  }, [isInView, lines]);

  const getLineColor = (type: string) => {
    switch (type) {
      case 'command': return 'text-white';
      case 'output': return 'text-white/60';
      case 'comment': return 'text-white/30';
      case 'success': return 'text-emerald-400';
      case 'file': return 'text-cyan-400';
      default: return 'text-white/60';
    }
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
      className={`terminal-window rounded-2xl overflow-hidden border border-white/10 bg-[#0c0c0c] ${className}`}
    >
      {/* Terminal header */}
      <div className="flex items-center gap-2 px-4 py-3 bg-white/[0.02] border-b border-white/5">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
          <div className="w-3 h-3 rounded-full bg-[#febc2e]" />
          <div className="w-3 h-3 rounded-full bg-[#28c840]" />
        </div>
        <span className="ml-2 text-xs text-white/30 font-mono">{title}</span>
      </div>

      {/* Terminal content */}
      <div className="p-5 font-mono text-sm space-y-2 min-h-[200px]">
        {lines.slice(0, visibleLines).map((line, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className={`${getLineColor(line.type)} ${line.type === 'command' ? 'flex items-center gap-2' : ''}`}
          >
            {line.type === 'command' && <span className="text-emerald-400">$</span>}
            {line.type === 'file' && <span className="text-white/30 mr-2">→</span>}
            <span>{line.content}</span>
            {line.type === 'command' && i === visibleLines - 1 && (
              <motion.span
                animate={{ opacity: [1, 0] }}
                transition={{ duration: 0.8, repeat: Infinity }}
                className="w-2 h-4 bg-white/80 ml-1"
              />
            )}
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

// ============================================================================
// COMPARISON BLOCK - BEFORE vs AFTER
// ============================================================================

const ComparisonBlock: FC = () => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <div ref={ref} className="grid md:grid-cols-2 gap-6">
      {/* WITHOUT ENGRAM */}
      <motion.div
        initial={{ opacity: 0, x: -30 }}
        animate={isInView ? { opacity: 1, x: 0 } : {}}
        transition={{ duration: 0.6 }}
        className="relative rounded-2xl border border-red-500/20 bg-red-500/[0.02] p-6 overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/10 blur-3xl" />
        <div className="relative">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <span className="text-sm font-medium text-red-400">Without Engram</span>
          </div>
          <div className="space-y-3 font-mono text-xs">
            <div className="p-3 rounded-lg bg-black/40 border border-white/5">
              <p className="text-white/40">Claude: "I don't have access to your codebase"</p>
            </div>
            <div className="p-3 rounded-lg bg-black/40 border border-white/5">
              <p className="text-white/40">Cursor: "Context limit exceeded"</p>
            </div>
            <div className="p-3 rounded-lg bg-black/40 border border-white/5">
              <p className="text-white/40">You: *re-explains architecture for the 10th time*</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* WITH ENGRAM */}
      <motion.div
        initial={{ opacity: 0, x: 30 }}
        animate={isInView ? { opacity: 1, x: 0 } : {}}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="relative rounded-2xl border border-emerald-500/20 bg-emerald-500/[0.02] p-6 overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 blur-3xl" />
        <div className="relative">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="text-sm font-medium text-emerald-400">With Engram</span>
          </div>
          <div className="space-y-3 font-mono text-xs">
            <div className="p-3 rounded-lg bg-black/40 border border-emerald-500/10">
              <p className="text-emerald-400/80">"Based on your auth middleware at line 47..."</p>
            </div>
            <div className="p-3 rounded-lg bg-black/40 border border-emerald-500/10">
              <p className="text-emerald-400/80">"You updated this 3 days ago in commit a3f2d..."</p>
            </div>
            <div className="p-3 rounded-lg bg-black/40 border border-emerald-500/10">
              <p className="text-emerald-400/80">"Here's how it connects to your login flow..."</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

// ============================================================================
// FLOATING STAT CARD
// ============================================================================

const FloatingStat: FC<{
  value: string;
  label: string;
  position: { top?: string; bottom?: string; left?: string; right?: string };
  delay?: number;
}> = ({ value, label, position, delay = 0 }) => {
  return (
    <motion.div
      className="floating-stat"
      style={position}
      initial={{ opacity: 0, y: 30, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 1, delay: delay + 1.5, ease: [0.16, 1, 0.3, 1] }}
    >
      <motion.div
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      >
        <p className="stat-value">{value}</p>
        <p className="stat-label">{label}</p>
      </motion.div>
    </motion.div>
  );
};

// ============================================================================
// NAVBAR
// ============================================================================

const Navbar: FC = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <motion.nav
      className="navbar"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
    >
      <a href="/" className="nav-logo" data-cursor-hover>
        <div className="logo-icon">
          <span />
        </div>
        <span>Engram</span>
      </a>

      <div className="nav-links">
        <a href="#features" className="nav-link" data-cursor-hover>Features</a>
        <a href="#how" className="nav-link" data-cursor-hover>How it works</a>
        <a href="#docs" className="nav-link" data-cursor-hover>Docs</a>
        <a
          href="https://github.com/Tobbiloba/engram"
          target="_blank"
          rel="noreferrer"
          className="nav-cta"
          data-cursor-hover
        >
          Get Started
        </a>
      </div>

      <button
        className="mobile-menu-btn"
        onClick={() => setMenuOpen(!menuOpen)}
        data-cursor-hover
      >
        <motion.span animate={{ rotate: menuOpen ? 45 : 0, y: menuOpen ? 7 : 0 }} />
        <motion.span animate={{ opacity: menuOpen ? 0 : 1 }} />
        <motion.span animate={{ rotate: menuOpen ? -45 : 0, y: menuOpen ? -7 : 0 }} />
      </button>
    </motion.nav>
  );
};

// ============================================================================
// HERO SECTION
// ============================================================================

const HeroSection: FC = () => {
  const containerRef = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], [0, 300]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  return (
    <section ref={containerRef} className="hero">
      {/* Background elements */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />
      <div className="grid-bg" />
      <Particles />

      {/* Main content */}
      <motion.div style={{ y, opacity }} className="relative z-10 px-6 md:px-12 lg:px-20">
        <div className="max-w-[1400px] mx-auto">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="mb-8"
          >
            <span className="floating-badge">
              <span className="badge-dot" />
              <span>Memory Layer for AI</span>
            </span>
          </motion.div>

          {/* Main headline */}
          <MouseParallax intensity={0.02}>
            <h1 className="headline mb-8">
              <TextReveal delay={0.2}>Your AI</TextReveal>
              <TextReveal delay={0.35} className="text-outline">Finally</TextReveal>
              <TextReveal delay={0.5} className="text-gradient">Remembers</TextReveal>
            </h1>
          </MouseParallax>

          {/* Subtitle */}
          <motion.p
            className="subtitle mb-12"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 1, ease: [0.16, 1, 0.3, 1] }}
          >
            Persistent context for your codebase. Architecture decisions, recent changes,
            and project intent—available in every AI conversation.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            className="flex flex-wrap items-center gap-4"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 1.2, ease: [0.16, 1, 0.3, 1] }}
          >
            <MagneticButton href="https://github.com/Tobbiloba/engram" variant="primary">
              <span>Get Started</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </MagneticButton>

            <MagneticButton href="#features" variant="secondary">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="12" r="10" />
                <polygon points="10 8 16 12 10 16 10 8" fill="currentColor" />
              </svg>
              <span>Watch Demo</span>
            </MagneticButton>
          </motion.div>
        </div>

        {/* Floating stats */}
        <MouseParallax intensity={-0.03} className="hidden lg:block">
          <FloatingStat
            value="10k+"
            label="Files Indexed"
            position={{ top: "10%", right: "10%" }}
            delay={0}
          />
        </MouseParallax>

        <MouseParallax intensity={0.04} className="hidden lg:block">
          <FloatingStat
            value="89ms"
            label="Avg Response"
            position={{ bottom: "20%", right: "15%" }}
            delay={0.2}
          />
        </MouseParallax>

        <MouseParallax intensity={-0.05} className="hidden xl:block">
          <FloatingStat
            value="100%"
            label="Local First"
            position={{ top: "30%", right: "25%" }}
            delay={0.4}
          />
        </MouseParallax>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        className="scroll-indicator"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 2 }}
      >
        <span className="scroll-text">Scroll</span>
        <div className="scroll-line" />
      </motion.div>
    </section>
  );
};

// ============================================================================
// PROBLEM SECTION - THE PAIN
// ============================================================================

const ProblemSection: FC = () => {
  return (
    <section id="problem" className="section bg-black relative overflow-hidden">
      <div className="orb orb-2" style={{ top: "-30%", left: "-20%", opacity: 0.3 }} />

      <div className="max-w-[1200px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mb-16"
        >
          <span className="text-red-400/80 text-sm font-medium uppercase tracking-widest">The Problem</span>
          <h2 className="mt-4 text-4xl md:text-5xl lg:text-6xl font-semibold tracking-tight leading-[1.1]">
            Every conversation
            <br />
            <span className="text-white/30">starts from zero.</span>
          </h2>
        </motion.div>

        <ComparisonBlock />

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-12 grid grid-cols-3 gap-8 py-8 border-t border-white/5"
        >
          {[
            { value: "5 min", label: "Average context window" },
            { value: "73%", label: "Time spent re-explaining" },
            { value: "∞", label: "Times you've said 'as I mentioned'" },
          ].map((stat, i) => (
            <div key={i} className="text-center">
              <p className="text-2xl md:text-3xl font-bold text-white/20">{stat.value}</p>
              <p className="mt-1 text-xs text-white/40">{stat.label}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

// ============================================================================
// FEATURES SECTION - REAL DEMOS
// ============================================================================

const FeaturesSection: FC = () => {
  return (
    <section id="features" className="bg-black relative">
      {/* Feature 1: Semantic Search */}
      <div className="section border-t border-white/5">
        <div className="max-w-[1200px] mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                  <svg className="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <span className="text-sm text-cyan-400 font-medium">Semantic Search</span>
              </div>
              <h3 className="text-3xl md:text-4xl font-semibold tracking-tight leading-tight">
                Ask in plain English.
                <br />
                <span className="text-white/40">Get precise results.</span>
              </h3>
              <p className="mt-4 text-white/50 leading-relaxed">
                No more grep gymnastics. Ask "where do we handle auth errors" and get exactly what you need—with relevance scores.
              </p>
            </motion.div>

            <AnimatedTerminal
              title="engram query"
              lines={[
                { type: 'command', content: 'engram query "where do we handle authentication errors"', delay: 600 },
                { type: 'comment', content: '', delay: 300 },
                { type: 'output', content: 'Searching 2,847 files...', delay: 400 },
                { type: 'comment', content: '', delay: 200 },
                { type: 'file', content: 'src/middleware/auth.ts:47         94% match', delay: 300 },
                { type: 'file', content: 'src/api/auth/login.ts:23          89% match', delay: 200 },
                { type: 'file', content: 'src/utils/errors.ts:156           82% match', delay: 200 },
                { type: 'comment', content: '', delay: 200 },
                { type: 'success', content: '✓ 3 results in 127ms', delay: 300 },
              ]}
            />
          </div>
        </div>
      </div>

      {/* Feature 2: Temporal Memory */}
      <div className="section border-t border-white/5">
        <div className="max-w-[1200px] mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="lg:order-2"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
                  <svg className="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <span className="text-sm text-violet-400 font-medium">Git-Aware Context</span>
              </div>
              <h3 className="text-3xl md:text-4xl font-semibold tracking-tight leading-tight">
                Knows what changed.
                <br />
                <span className="text-white/40">And when.</span>
              </h3>
              <p className="mt-4 text-white/50 leading-relaxed">
                Engram reads your git history. Recent changes rank higher. Your AI knows what you touched yesterday, not just what exists.
              </p>
            </motion.div>

            <AnimatedTerminal
              title="engram whats_changed"
              className="lg:order-1"
              lines={[
                { type: 'command', content: 'engram whats_changed --days 7', delay: 600 },
                { type: 'comment', content: '', delay: 300 },
                { type: 'output', content: 'Analyzing git history...', delay: 400 },
                { type: 'comment', content: '', delay: 200 },
                { type: 'output', content: '📁 auth/middleware.ts', delay: 300 },
                { type: 'output', content: '   └─ 3 commits, last: "fix token refresh"', delay: 200 },
                { type: 'output', content: '📁 api/users.ts', delay: 200 },
                { type: 'output', content: '   └─ 5 commits, last: "add rate limiting"', delay: 200 },
                { type: 'output', content: '📁 lib/db.ts', delay: 200 },
                { type: 'output', content: '   └─ 2 commits, last: "connection pooling"', delay: 200 },
                { type: 'comment', content: '', delay: 200 },
                { type: 'success', content: '✓ 12 files changed across 18 commits', delay: 300 },
              ]}
            />
          </div>
        </div>
      </div>

      {/* Feature 3: Local First */}
      <div className="section border-t border-white/5">
        <div className="max-w-[1200px] mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                  <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                  </svg>
                </div>
                <span className="text-sm text-emerald-400 font-medium">100% Local</span>
              </div>
              <h3 className="text-3xl md:text-4xl font-semibold tracking-tight leading-tight">
                Your code stays yours.
                <br />
                <span className="text-white/40">Always.</span>
              </h3>
              <p className="mt-4 text-white/50 leading-relaxed">
                No cloud uploads. No API calls with your source code. Everything runs on your machine. Your proprietary code never leaves.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                {['No cloud', 'No uploads', 'No tracking', 'Open source'].map((tag) => (
                  <span key={tag} className="px-3 py-1.5 text-xs font-medium text-emerald-400/80 bg-emerald-500/10 rounded-full border border-emerald-500/20">
                    {tag}
                  </span>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="relative"
            >
              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/[0.02] p-8">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                    <svg className="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-white">Privacy First Architecture</p>
                    <p className="text-sm text-white/40">All processing happens locally</p>
                  </div>
                </div>
                <div className="space-y-3">
                  {[
                    { label: 'Data sent to cloud', value: '0 bytes' },
                    { label: 'External API calls', value: 'None' },
                    { label: 'Index location', value: '~/.engram/local' },
                  ].map((item) => (
                    <div key={item.label} className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
                      <span className="text-sm text-white/40">{item.label}</span>
                      <span className="text-sm text-emerald-400 font-mono">{item.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// HOW IT WORKS
// ============================================================================

const HowItWorks: FC = () => {
  return (
    <section id="how" className="section bg-black relative overflow-hidden">
      <div className="orb orb-1" style={{ bottom: "-40%", right: "-20%" }} />

      <div className="max-w-[1400px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 60 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="text-center mb-20"
        >
          <span className="floating-badge mb-6 inline-flex">
            <span className="badge-dot" />
            <span>How it works</span>
          </span>
          <h2 className="text-4xl md:text-6xl lg:text-7xl font-semibold tracking-tight leading-[1.1]">
            Three commands.
            <br />
            <span className="text-gradient">Instant context.</span>
          </h2>
        </motion.div>

        {/* Steps */}
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { step: "01", title: "Index", cmd: "engram init ~/project", desc: "Scan and index your codebase" },
            { step: "02", title: "Configure", cmd: "engram setup", desc: "Connect to your AI tools" },
            { step: "03", title: "Query", cmd: "engram query \"...\"", desc: "Ask questions naturally" },
          ].map((item, i) => (
            <motion.div
              key={item.step}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: i * 0.15, ease: [0.16, 1, 0.3, 1] }}
              className="relative"
            >
              <span className="text-8xl font-bold text-white/[0.03] absolute -top-8 -left-2">
                {item.step}
              </span>
              <div className="relative p-8 rounded-2xl border border-white/5 bg-white/[0.02]">
                <h3 className="text-2xl font-semibold mb-2">{item.title}</h3>
                <p className="text-white/40 mb-6">{item.desc}</p>
                <div className="p-4 rounded-xl bg-black border border-white/10 font-mono text-sm">
                  <span className="text-cyan-300">$</span>{" "}
                  <span className="text-white/80">{item.cmd}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// CTA SECTION
// ============================================================================

const CTASection: FC = () => {
  return (
    <section className="section bg-black relative overflow-hidden">
      <div className="orb orb-3" style={{ top: "50%", left: "50%", transform: "translate(-50%, -50%)" }} />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        className="max-w-4xl mx-auto text-center relative z-10"
      >
        <h2 className="text-4xl md:text-6xl lg:text-7xl font-semibold tracking-tight leading-[1.1] mb-6">
          Ready to give your AI
          <br />
          <span className="text-gradient">a memory upgrade?</span>
        </h2>
        <p className="text-lg text-white/40 max-w-xl mx-auto mb-10">
          Start indexing your codebase in under 2 minutes.
          Free, open-source, and built for privacy.
        </p>
        <MagneticButton href="https://github.com/Tobbiloba/engram" variant="primary">
          <span>Get Started Free</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </MagneticButton>
      </motion.div>
    </section>
  );
};

// ============================================================================
// FOOTER
// ============================================================================

const Footer: FC = () => {
  return (
    <footer className="py-12 px-6 md:px-12 lg:px-20 border-t border-white/5">
      <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
        <a href="/" className="nav-logo" data-cursor-hover>
          <div className="logo-icon">
            <span />
          </div>
          <span>Engram</span>
        </a>

        <div className="flex items-center gap-8 text-sm text-white/40">
          <a href="#" className="hover:text-white transition-colors" data-cursor-hover>Docs</a>
          <a href="https://github.com/Tobbiloba/engram" target="_blank" rel="noreferrer" className="hover:text-white transition-colors" data-cursor-hover>GitHub</a>
          <a href="#" className="hover:text-white transition-colors" data-cursor-hover>Twitter</a>
        </div>

        <p className="text-sm text-white/20">MIT Licensed</p>
      </div>
    </footer>
  );
};

// ============================================================================
// MAIN PAGE
// ============================================================================

const Home: FC = () => {
  return (
    <>
      <CustomCursor />
      <div className="noise" />
      <main className="bg-black text-white overflow-x-hidden">
        <Navbar />
        <HeroSection />
        <ProblemSection />
        <FeaturesSection />
        <HowItWorks />
        <CTASection />
        <Footer />
      </main>
    </>
  );
};

export default Home;
