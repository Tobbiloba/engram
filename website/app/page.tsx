"use client";

import { FC, useRef, useEffect, useState, useCallback } from "react";
import { motion, useMotionValue, useSpring, useTransform, useScroll, AnimatePresence } from "framer-motion";

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
            className="flex flex-wrap items-center gap-6"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 1.2, ease: [0.16, 1, 0.3, 1] }}
          >
            <a
              href="https://github.com/Tobbiloba/engram"
              target="_blank"
              rel="noreferrer"
              className="cta-btn"
              data-cursor-hover
            >
              <span>Get Started</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </a>

            <a href="#demo" className="link-underline" data-cursor-hover>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="12" r="10" />
                <polygon points="10 8 16 12 10 16 10 8" fill="currentColor" />
              </svg>
              <span>Watch Demo</span>
            </a>
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
// FEATURES PREVIEW (to show there's more content)
// ============================================================================

const FeaturesPreview: FC = () => {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], [100, -100]);

  return (
    <section ref={ref} id="features" className="section bg-black relative overflow-hidden">
      <div className="orb orb-2" style={{ top: "-30%", left: "-20%" }} />

      <motion.div style={{ y }} className="max-w-[1400px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 60 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="text-center mb-20"
        >
          <span className="floating-badge mb-6 inline-flex">
            <span className="badge-dot" />
            <span>Features</span>
          </span>
          <h2 className="text-4xl md:text-6xl lg:text-7xl font-semibold tracking-tight leading-[1.1]">
            Everything you need.
            <br />
            <span className="text-outline">Nothing you don't.</span>
          </h2>
        </motion.div>

        {/* Feature grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            {
              title: "Semantic Search",
              desc: "Natural language queries across your entire codebase. Find what matters instantly.",
              icon: "🔍",
            },
            {
              title: "Git-Aware Context",
              desc: "Understands your commit history. Prioritizes what changed recently.",
              icon: "⏱",
            },
            {
              title: "Local-First",
              desc: "Your code stays on your machine. Zero cloud dependency.",
              icon: "🔒",
            },
            {
              title: "MCP Integration",
              desc: "Works seamlessly with Claude, Cursor, and other AI tools.",
              icon: "⚡",
            },
            {
              title: "Instant Indexing",
              desc: "Index 10,000+ files in under 2 minutes. Incremental updates.",
              icon: "📁",
            },
            {
              title: "Smart Retrieval",
              desc: "Combines semantic similarity with temporal relevance.",
              icon: "🧠",
            },
          ].map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="group p-8 rounded-2xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] hover:border-white/10 transition-all duration-500"
              data-cursor-hover
            >
              <span className="text-3xl mb-4 block">{feature.icon}</span>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-white/40 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>
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
        <a
          href="https://github.com/Tobbiloba/engram"
          target="_blank"
          rel="noreferrer"
          className="cta-btn"
          data-cursor-hover
        >
          <span>Get Started Free</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </a>
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
        <FeaturesPreview />
        <HowItWorks />
        <CTASection />
        <Footer />
      </main>
    </>
  );
};

export default Home;
