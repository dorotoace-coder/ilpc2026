import { useState } from "react";
import { MessageCircle, ChevronDown } from "lucide-react";

const designations = [
  "Pastor", "Bishop", "Apostle", "Prophet", "Prophetess",
  "Evangelist", "Deacon", "Deaconess", "Elder", "Reverend",
  "Church Leader", "Minister", "Missionary", "Christian Worker", "Other",
];

const WHATSAPP_NUMBER = "2348122166179";

const RegistrationForm = () => {
  const [formData, setFormData] = useState({
    fullName: "",
    ministry: "",
    designation: "",
    desire: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const message =
      `Hello! I would like to register for ILPC 2026 — Fresh Oil for a New Season.%0A%0A` +
      `*Name:* ${formData.fullName}%0A` +
      `*Ministry/Church:* ${formData.ministry}%0A` +
      `*Designation:* ${formData.designation}%0A` +
      `*My Desire:* ${formData.desire}`;
    window.open(`https://wa.me/${WHATSAPP_NUMBER}?text=${message}`, "_blank");
  };

  return (
    <div className="w-full max-w-md mx-auto mb-10">
      <div className="text-center mb-5">
        <p className="text-[#C9972A] text-xs font-semibold tracking-widest uppercase mb-3">
          Join Us
        </p>
        <h3 className="text-2xl sm:text-3xl font-bold text-white mb-2">
          Register Now
        </h3>
        <p className="text-white/50 text-sm">
          Fill in your details — we'll open WhatsApp to complete your registration
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="rounded-2xl p-6 sm:p-8 card-3d"
        style={{
          background: "linear-gradient(135deg, rgba(155,114,170,0.15) 0%, rgba(45,10,78,0.7) 50%, rgba(155,114,170,0.1) 100%)",
          border: "1px solid rgba(155,114,170,0.25)",
        }}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-[#B88FC7] text-xs font-semibold tracking-wider uppercase mb-1.5">
              Full Name
            </label>
            <input
              type="text"
              name="fullName"
              required
              value={formData.fullName}
              onChange={handleChange}
              placeholder="Enter your full name"
              className="w-full px-4 py-3 rounded-xl text-sm text-white placeholder-white/30 outline-none transition-all duration-300 focus:ring-2 focus:ring-[#9B72AA]/50"
              style={{ background: "rgba(155,114,170,0.1)", border: "1px solid rgba(155,114,170,0.2)" }}
            />
          </div>

          <div>
            <label className="block text-[#B88FC7] text-xs font-semibold tracking-wider uppercase mb-1.5">
              Ministry / Church
            </label>
            <input
              type="text"
              name="ministry"
              required
              value={formData.ministry}
              onChange={handleChange}
              placeholder="Your ministry or church name"
              className="w-full px-4 py-3 rounded-xl text-sm text-white placeholder-white/30 outline-none transition-all duration-300 focus:ring-2 focus:ring-[#9B72AA]/50"
              style={{ background: "rgba(155,114,170,0.1)", border: "1px solid rgba(155,114,170,0.2)" }}
            />
          </div>

          <div className="relative">
            <label className="block text-[#B88FC7] text-xs font-semibold tracking-wider uppercase mb-1.5">
              Designation
            </label>
            <div className="relative">
              <select
                name="designation"
                required
                value={formData.designation}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl text-sm text-white outline-none appearance-none transition-all duration-300 focus:ring-2 focus:ring-[#9B72AA]/50 cursor-pointer"
                style={{ background: "rgba(45,10,78,0.9)", border: "1px solid rgba(155,114,170,0.2)" }}
              >
                <option value="" disabled style={{ background: "#2D0A4E", color: "#B88FC7" }}>
                  Select your designation
                </option>
                {designations.map((d) => (
                  <option key={d} value={d} style={{ background: "#2D0A4E", color: "#fff" }}>
                    {d}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#9B72AA] pointer-events-none" />
            </div>
          </div>

          <div>
            <label className="block text-[#B88FC7] text-xs font-semibold tracking-wider uppercase mb-1.5">
              What do you desire from ILPC 2026?
            </label>
            <textarea
              name="desire"
              required
              value={formData.desire}
              onChange={handleChange}
              placeholder="Share your expectation or prayer request..."
              rows={3}
              className="w-full px-4 py-3 rounded-xl text-sm text-white placeholder-white/30 outline-none transition-all duration-300 focus:ring-2 focus:ring-[#9B72AA]/50 resize-none"
              style={{ background: "rgba(155,114,170,0.1)", border: "1px solid rgba(155,114,170,0.2)" }}
            />
          </div>
        </div>

        <button
          type="submit"
          className="w-full mt-6 bg-[#25D366] hover:bg-[#20BD5A] text-white py-3.5 rounded-xl font-bold text-sm tracking-wide hover:shadow-lg hover:shadow-[#25D366]/30 transition-all duration-300 hover:scale-[1.02] flex items-center justify-center gap-2"
        >
          <MessageCircle className="w-4 h-4" />
          Send via WhatsApp
        </button>

        <p className="text-white/30 text-[10px] text-center mt-3">
          Free registration • Opens WhatsApp to complete
        </p>
      </form>
    </div>
  );
};

export default RegistrationForm;
