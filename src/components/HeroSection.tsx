import CountdownTimer from "./CountdownTimer";
import { Droplets, ChevronDown } from "lucide-react";

const HeroSection = () => {
  const scrollToSchedule = () => {
    const el = document.querySelector("#schedule");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section
      id="home"
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
      style={{ background: "linear-gradient(160deg, #1A0533 0%, #2D0A4E 40%, #3D1560 100%)" }}
    >
      {/* Decorative floating orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 rounded-full bg-[#C9972A]/5 blur-3xl animate-float" />
        <div className="absolute bottom-20 right-10 w-96 h-96 rounded-full bg-[#C9972A]/5 blur-3xl animate-float-delayed" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full border border-[#C9972A]/10 animate-rotate-slow" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full border border-[#C9972A]/5 animate-rotate-slow" style={{ animationDirection: "reverse", animationDuration: "25s" }} />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 text-center pt-24 pb-16">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 glass rounded-full px-5 py-2 mb-8 animate-fade-in-up">
          <Droplets className="w-4 h-4 text-[#C9972A]" />
          <span className="text-[#C9972A] text-xs sm:text-sm font-semibold tracking-widest uppercase">
            June 5–7, 2026 • Akute, Nigeria
          </span>
        </div>

        {/* Title */}
        <h1 className="text-5xl sm:text-7xl lg:text-8xl font-black text-white leading-tight mb-4 animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
          ILPC <span className="gold-text">2026</span>
        </h1>

        <p className="text-base sm:text-lg text-white/50 font-medium tracking-widest uppercase mb-6 animate-fade-in-up" style={{ animationDelay: "0.35s" }}>
          International Leaders & Pastors Conference
        </p>

        {/* Theme */}
        <div className="perspective-1000 mb-12 animate-fade-in-up" style={{ animationDelay: "0.5s" }}>
          <div className="inline-block glass rounded-2xl px-8 sm:px-12 py-5 sm:py-6 card-3d animate-pulse-gold">
            <p className="text-xs sm:text-sm text-[#C9972A]/80 font-semibold tracking-widest uppercase mb-1">
              Conference Theme
            </p>
            <h2 className="text-2xl sm:text-4xl font-bold gold-text italic">
              "Fresh Oil for a New Season"
            </h2>
          </div>
        </div>

        {/* Host */}
        <p className="text-white/60 text-sm sm:text-base mb-10 animate-fade-in-up" style={{ animationDelay: "0.65s" }}>
          Hosted by <span className="text-white font-semibold">Pastor Amos Unogwu</span> — HBG Ministry, Akute Nigeria
        </p>

        {/* Countdown */}
        <div className="mb-12 animate-fade-in-up" style={{ animationDelay: "0.8s" }}>
          <p className="text-white/40 text-xs uppercase tracking-widest mb-4 font-medium">
            Countdown to Conference
          </p>
          <CountdownTimer />
        </div>

        {/* CTA */}
        <div className="animate-fade-in-up" style={{ animationDelay: "0.95s" }}>
          <a
            href="#register"
            className="inline-block gold-gradient text-[#2D0A4E] px-10 py-4 rounded-full font-bold text-base sm:text-lg tracking-wide hover:shadow-xl hover:shadow-[#C9972A]/30 transition-all duration-300 hover:scale-105"
          >
            Register Now
          </a>
        </div>

        {/* Scroll indicator */}
        <button
          onClick={scrollToSchedule}
          className="mt-16 inline-flex flex-col items-center text-white/30 hover:text-[#C9972A] transition-colors animate-fade-in-up"
          style={{ animationDelay: "1.1s" }}
        >
          <span className="text-[10px] uppercase tracking-widest mb-2">Explore</span>
          <ChevronDown className="w-5 h-5 animate-bounce" />
        </button>
      </div>
    </section>
  );
};

export default HeroSection;