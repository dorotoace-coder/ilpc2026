import { Droplets, Heart } from "lucide-react";

const Footer = () => {
  return (
    <footer
      className="relative py-12 overflow-hidden"
      style={{ background: "#110222" }}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex flex-col items-center text-center">
          {/* Logo */}
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-full gold-gradient flex items-center justify-center text-[#2D0A4E] font-bold text-sm">
              I
            </div>
            <span className="text-white font-bold text-lg tracking-wide">
              ILPC <span className="gold-text">2026</span>
            </span>
          </div>

          <div className="flex items-center gap-2 text-white/40 text-xs sm:text-sm mb-4">
            <Droplets className="w-3.5 h-3.5 text-[#C9972A]" />
            <span className="italic">"Fresh Oil for a New Season"</span>
          </div>

          <p className="text-white/30 text-xs sm:text-sm mb-6 max-w-md leading-relaxed">
            International Leaders & Pastors Conference — June 5–7, 2026
            <br />
            HBG Ministry, Akute, Ogun State, Nigeria
            <br />
            Host: Pastor Amos Unogwu
          </p>

          <div className="w-16 h-px bg-[#C9972A]/20 mb-6" />

          <p className="text-white/20 text-xs flex items-center gap-1">
            Made with <Heart className="w-3 h-3 text-[#C9972A]/50" /> for the Kingdom
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;