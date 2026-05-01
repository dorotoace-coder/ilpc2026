import { useState } from "react";
import { ChevronDown, HelpCircle } from "lucide-react";

const faqs = [
  {
    q: "Is there a registration fee?",
    a: "No! ILPC 2026 is completely free to attend. We believe that the anointing should be accessible to every leader God is calling.",
  },
  {
    q: "Can I attend if I'm not a pastor?",
    a: "Absolutely! While the conference is geared toward leaders and pastors, every believer who hungers for a fresh encounter with God is welcome.",
  },
  {
    q: "Will there be accommodation?",
    a: "We are working with local hotels to secure discounted rates for attendees. Details will be shared upon registration confirmation via WhatsApp.",
  },
  {
    q: "Is the conference available online?",
    a: "Selected sessions will be streamed live on our social media platforms. However, we strongly encourage in-person attendance for the full impartation experience.",
  },
  {
    q: "What should I bring?",
    a: "Bring your Bible, a journal, an expectant heart, and comfortable clothing. All conference materials will be provided at the venue.",
  },
  {
    q: "How do I get to the venue?",
    a: "HBG Ministry is located in Akute, Ogun State — about 30 minutes from Ikeja, Lagos. You can reach it via public transport or ride-hailing apps. Contact us on WhatsApp for detailed directions.",
  },
];

const FAQItem = ({ q, a, isOpen, onToggle }: { q: string; a: string; isOpen: boolean; onToggle: () => void }) => {
  return (
    <div
      className="rounded-xl overflow-hidden transition-all duration-300"
      style={{
        background: isOpen
          ? "linear-gradient(135deg, rgba(155, 114, 170, 0.15) 0%, rgba(45, 10, 78, 0.5) 100%)"
          : "rgba(155, 114, 170, 0.06)",
        border: isOpen
          ? "1px solid rgba(155, 114, 170, 0.3)"
          : "1px solid rgba(155, 114, 170, 0.12)",
      }}
    >
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-5 sm:px-6 py-4 text-left"
      >
        <span className="text-white font-semibold text-sm sm:text-base pr-4">{q}</span>
        <ChevronDown
          className={`w-4 h-4 text-[#9B72AA] shrink-0 transition-transform duration-300 ${
            isOpen ? "rotate-180 text-[#C9972A]" : ""
          }`}
        />
      </button>
      {isOpen && (
        <div className="px-5 sm:px-6 pb-5 animate-fade-in-up">
          <p className="text-white/55 text-sm leading-relaxed">{a}</p>
        </div>
      )}
    </div>
  );
};

const FAQSection = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section
      className="relative py-24 overflow-hidden"
      style={{ background: "linear-gradient(180deg, #1A0533 0%, #2D0A4E 50%, #1A0533 100%)" }}
    >
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute bottom-0 left-1/3 w-80 h-80 rounded-full bg-[#9B72AA]/4 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-2xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <div className="w-12 h-12 rounded-xl gold-gradient flex items-center justify-center mx-auto mb-5">
            <HelpCircle className="w-6 h-6 text-[#2D0A4E]" />
          </div>
          <p className="text-[#C9972A] text-xs sm:text-sm font-semibold tracking-widest uppercase mb-3">
            Got Questions?
          </p>
          <h2 className="text-3xl sm:text-5xl font-bold text-white mb-4">
            Frequently Asked
          </h2>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, i) => (
            <FAQItem
              key={i}
              q={faq.q}
              a={faq.a}
              isOpen={openIndex === i}
              onToggle={() => setOpenIndex(openIndex === i ? null : i)}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default FAQSection;