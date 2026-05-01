import { MessageCircle, CheckCircle } from "lucide-react";
import SpotifySection from "./SpotifySection";
import RegistrationForm from "./RegistrationForm";

const benefits = [
  "3 days of powerful ministrations",
  "Prophetic impartation & anointing",
  "Leadership masterclasses",
  "Networking with kingdom leaders",
  "Free conference materials",
];

const RegisterSection = () => {
  const whatsappLink =
    "https://wa.me/2348000000000?text=Hello%2C%20I%20would%20like%20to%20register%20for%20ILPC%202026%20-%20Fresh%20Oil%20for%20a%20New%20Season";

  return (
    <section
      id="register"
      className="relative py-24 overflow-hidden"
      style={{ background: "linear-gradient(180deg, #1A0533 0%, #2D0A4E 100%)" }}
    >
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute bottom-0 right-0 w-96 h-96 rounded-full bg-[#9B72AA]/5 blur-3xl" />
        <div className="absolute top-0 left-1/4 w-72 h-72 rounded-full bg-[#C9972A]/3 blur-3xl" />
        <div className="absolute bottom-1/3 left-0 w-80 h-80 rounded-full bg-[#9B72AA]/3 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 text-center">
        <p className="text-[#C9972A] text-xs sm:text-sm font-semibold tracking-widest uppercase mb-3">
          Secure Your Place
        </p>
        <h2 className="text-3xl sm:text-5xl font-bold text-white mb-4">
          Register for ILPC 2026
        </h2>
        <p className="text-white/60 max-w-xl mx-auto text-base sm:text-lg mb-10 leading-relaxed">
          Don't miss this divine appointment. Register now 
          and secure your place at the conference.
        </p>

        {/* Benefits */}
        <div
          className="rounded-2xl p-6 sm:p-8 mb-10 max-w-md mx-auto card-3d"
          style={{
            background: "linear-gradient(135deg, rgba(155, 114, 170, 0.15) 0%, rgba(45, 10, 78, 0.6) 50%, rgba(201, 151, 42, 0.08) 100%)",
            border: "1px solid rgba(155, 114, 170, 0.2)",
          }}
        >
          <p className="text-[#C9972A] text-xs font-semibold tracking-widest uppercase mb-5">
            What to Expect
          </p>
          <div className="space-y-3 text-left">
            {benefits.map((b) => (
              <div key={b} className="flex items-center gap-3">
                <CheckCircle className="w-4 h-4 text-[#C9972A] shrink-0" />
                <span className="text-white/70 text-sm">{b}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Spotify Section */}
        <SpotifySection />

        {/* Registration Form */}
        <RegistrationForm />

        {/* WhatsApp Button */}
        <div className="mb-4">
          <p className="text-white/40 text-xs uppercase tracking-widest mb-4 font-medium">
            Or register via
          </p>
          <a
            href={whatsappLink}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 bg-[#25D366] hover:bg-[#20BD5A] text-white px-8 sm:px-10 py-4 sm:py-5 rounded-full font-bold text-base sm:text-lg tracking-wide hover:shadow-xl hover:shadow-[#25D366]/30 transition-all duration-300 hover:scale-105"
          >
            <MessageCircle className="w-6 h-6" />
            Register via WhatsApp
          </a>
        </div>

        <p className="text-white/30 text-xs mt-6">
          Free registration • Spaces are limited
        </p>
      </div>
    </section>
  );
};

export default RegisterSection;