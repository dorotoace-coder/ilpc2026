import { Droplets, Heart, Phone, Mail, Instagram } from "lucide-react";

const Footer = () => {
  return (
    <footer
      className="relative py-16 overflow-hidden"
      style={{ background: "#110222" }}
    >
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-1 rounded-full" style={{
          background: "linear-gradient(90deg, transparent, rgba(201,151,42,0.3), transparent)"
        }} />
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex flex-col items-center text-center">
          {/* Logo */}
          <div className="flex items-center gap-2 mb-4">
            <div className="w-10 h-10 rounded-full gold-gradient flex items-center justify-center text-[#2D0A4E] font-bold text-base">
              I
            </div>
            <span className="text-white font-bold text-xl tracking-wide">
              ILPC <span className="gold-text">2026</span>
            </span>
          </div>

          <div className="flex items-center gap-2 text-white/40 text-sm mb-3">
            <Droplets className="w-4 h-4 text-[#C9972A]" />
            <span className="italic text-base">"Fresh Oil for a New Season"</span>
          </div>

          <p className="text-white/35 text-sm mb-6 max-w-md leading-relaxed">
            International Leaders & Pastors Conference
            <br />
            June 5–7, 2026 • HBG Ministry, Akute, Ogun State, Nigeria
          </p>

          {/* Contact Links */}
          <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6 mb-8">
            <a
              href="https://wa.me/2348000000000"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-white/50 hover:text-[#25D366] transition-colors text-sm"
            >
              <Phone className="w-4 h-4" />
              <span>WhatsApp</span>
            </a>
            <a
              href="mailto:info@ilpc2026.com"
              className="flex items-center gap-2 text-white/50 hover:text-[#C9972A] transition-colors text-sm"
            >
              <Mail className="w-4 h-4" />
              <span>info@ilpc2026.com</span>
            </a>
            <a
              href="https://instagram.com/ilpc2026"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-white/50 hover:text-[#E1306C] transition-colors text-sm"
            >
              <Instagram className="w-4 h-4" />
              <span>@ilpc2026</span>
            </a>
          </div>

          {/* Host */}
          <div className="rounded-xl px-6 py-3 mb-8" style={{
            background: "rgba(155, 114, 170, 0.08)",
            border: "1px solid rgba(155, 114, 170, 0.12)",
          }}>
            <p className="text-white/40 text-xs">
              Hosted by <span className="text-white/60 font-semibold">Pastor Amos Unogwu</span> — HBG Ministry International
            </p>
          </div>

          <div className="w-16 h-px bg-[#C9972A]/20 mb-6" />

          <p className="text-white/20 text-xs flex items-center gap-1">
            © 2026 ILPC • Made with <Heart className="w-3 h-3 text-[#C9972A]/50" /> for the Kingdom
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;