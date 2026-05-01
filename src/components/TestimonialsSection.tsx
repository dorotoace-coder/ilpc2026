import { Quote } from "lucide-react";

const testimonials = [
  {
    name: "Pastor Emmanuel Okafor",
    church: "Living Word Assembly, Lagos",
    text: "ILPC transformed my ministry. The fresh oil I received in the last conference is still burning — I came back refired and my congregation can feel the difference!",
  },
  {
    name: "Deaconess Mary Adebayo",
    church: "Grace Tabernacle, Ibadan",
    text: "The connections I made at ILPC opened doors I never imagined. This is not just a conference — it's a divine appointment that rewires your destiny.",
  },
  {
    name: "Bishop Dr. James Igwe",
    church: "Covenant Heritage, Abuja",
    text: "Every leader needs this encounter. The depth of teaching, the power of impartation, and the love among God's servants — there's nothing like ILPC.",
  },
];

const TestimonialsSection = () => {
  return (
    <section
      className="relative py-24 overflow-hidden"
      style={{ background: "linear-gradient(180deg, #1A0533 0%, #2D0A4E 100%)" }}
    >
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-80 h-80 rounded-full bg-[#9B72AA]/5 blur-3xl" />
        <div className="absolute bottom-1/4 right-0 w-72 h-72 rounded-full bg-[#C9972A]/4 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-16">
          <p className="text-[#C9972A] text-xs sm:text-sm font-semibold tracking-widest uppercase mb-3">
            Testimonies
          </p>
          <h2 className="text-3xl sm:text-5xl font-bold text-white mb-4">
            Lives Transformed
          </h2>
          <p className="text-white/60 max-w-xl mx-auto text-base sm:text-lg leading-relaxed">
            Hear from leaders whose ministries were forever changed at ILPC.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
          {testimonials.map((t, i) => (
            <div key={t.name} className="perspective-1000">
              <div
                className="rounded-2xl p-6 sm:p-8 card-3d h-full flex flex-col"
                style={{
                  background: "linear-gradient(135deg, rgba(155, 114, 170, 0.12) 0%, rgba(45, 10, 78, 0.6) 50%, rgba(201, 151, 42, 0.06) 100%)",
                  border: "1px solid rgba(155, 114, 170, 0.2)",
                }}
              >
                <Quote className="w-8 h-8 text-[#9B72AA]/30 mb-4 shrink-0" />
                <p className="text-white/60 text-sm sm:text-base leading-relaxed flex-1 mb-5 italic">
                  "{t.text}"
                </p>
                <div className="border-t border-[#9B72AA]/15 pt-4">
                  <p className="text-white font-bold text-sm">{t.name}</p>
                  <p className="text-[#B88FC7] text-xs">{t.church}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;