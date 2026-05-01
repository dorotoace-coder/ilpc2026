import { Droplets, BookOpen, Users } from "lucide-react";

const features = [
  {
    icon: Droplets,
    title: "Fresh Anointing",
    desc: "Experience a supernatural outpouring of fresh oil that will rejuvenate your ministry and empower your calling.",
  },
  {
    icon: BookOpen,
    title: "Sound Doctrine",
    desc: "Receive powerful teachings rooted in the Word that will equip you for the new season God is calling you into.",
  },
  {
    icon: Users,
    title: "Divine Connections",
    desc: "Connect with leaders and pastors from across the nations, forging relationships that will advance the Kingdom.",
  },
];

const AboutSection = () => {
  return (
    <section
      id="about"
      className="relative py-24 overflow-hidden"
      style={{ background: "linear-gradient(180deg, #2D0A4E 0%, #1A0533 100%)" }}
    >
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 right-0 w-80 h-80 rounded-full bg-[#C9972A]/3 blur-3xl" />
        <div className="absolute bottom-0 left-0 w-60 h-60 rounded-full bg-[#C9972A]/3 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-16">
          <p className="text-[#C9972A] text-xs sm:text-sm font-semibold tracking-widest uppercase mb-3">
            About the Conference
          </p>
          <h2 className="text-3xl sm:text-5xl font-bold text-white mb-6">
            A Holy Convocation
          </h2>
          <p className="text-white/60 max-w-2xl mx-auto text-base sm:text-lg leading-relaxed">
            The International Leaders and Pastors Conference (ILPC) is a divine gathering 
            where God's servants are refreshed, refired, and re-equipped for the assignment 
            ahead. This year, God is releasing <span className="text-[#C9972A] font-semibold">Fresh Oil</span> for 
            a <span className="text-[#C9972A] font-semibold">New Season</span> — come and partake.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
          {features.map((f, i) => (
            <div
              key={f.title}
              className="perspective-1000"
              style={{ animationDelay: `${i * 0.15}s` }}
            >
              <div className="glass rounded-2xl p-8 text-center card-3d h-full">
                <div className="w-14 h-14 rounded-xl gold-gradient flex items-center justify-center mx-auto mb-5">
                  <f.icon className="w-7 h-7 text-[#2D0A4E]" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{f.title}</h3>
                <p className="text-white/55 text-sm leading-relaxed">{f.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default AboutSection;