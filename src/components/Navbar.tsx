import { useState, useEffect } from "react";
import { Menu, X } from "lucide-react";

const navLinks = [
  { label: "Home", href: "#home" },
  { label: "About", href: "#about" },
  { label: "Schedule", href: "#schedule" },
  { label: "Register", href: "#register" },
];

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleNavClick = (href: string) => {
    setIsOpen(false);
    const el = document.querySelector(href);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled ? "glass shadow-lg py-3" : "py-5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <button
            onClick={() => handleNavClick("#home")}
            className="flex items-center gap-2 group"
          >
            <div className="w-10 h-10 rounded-full gold-gradient flex items-center justify-center text-[#2D0A4E] font-bold text-lg transition-transform group-hover:scale-110">
              I
            </div>
            <span className="text-white font-bold text-xl tracking-wide">
              ILPC <span className="gold-text">2026</span>
            </span>
          </button>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <button
                key={link.href}
                onClick={() => handleNavClick(link.href)}
                className="text-white/80 hover:text-[#C9972A] transition-colors duration-300 text-sm font-medium tracking-wide uppercase"
              >
                {link.label}
              </button>
            ))}
            <button
              onClick={() => handleNavClick("#register")}
              className="gold-gradient text-[#2D0A4E] px-6 py-2.5 rounded-full font-bold text-sm tracking-wide hover:shadow-lg hover:shadow-[#C9972A]/30 transition-all duration-300 hover:scale-105"
            >
              Register Now
            </button>
          </div>

          {/* Mobile toggle */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-white p-2"
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Nav */}
        {isOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-[#C9972A]/20 pt-4 animate-fade-in-up">
            <div className="flex flex-col gap-3">
              {navLinks.map((link) => (
                <button
                  key={link.href}
                  onClick={() => handleNavClick(link.href)}
                  className="text-white/80 hover:text-[#C9972A] transition-colors duration-300 text-left py-2 text-sm font-medium tracking-wide uppercase"
                >
                  {link.label}
                </button>
              ))}
              <button
                onClick={() => handleNavClick("#register")}
                className="gold-gradient text-[#2D0A4E] px-6 py-2.5 rounded-full font-bold text-sm tracking-wide mt-2 w-fit"
              >
                Register Now
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;