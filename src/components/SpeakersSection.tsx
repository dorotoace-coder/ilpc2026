import { Mic2 } from "lucide-react";

const speakers = [
  {
    name: "Pastor Amos Unogwu",
    title: "Host & Convener",
    church: "HBG Ministry, Akute",
    accent: "gold",
  },
  {
    name: "Bishop Dr. Samuel Adeyemi",
    title: "Keynote Speaker",
    church: "Covenant Heritage Ministry",
    accent: "lilac",
  },
  {
    name: "Prophetess Grace Ojo",
    title: "Guest Minister",
    church: "Fresh Fire Assembly",
    accent: "gold",
  },
  {
    name: "Apostle Chidi Nwosu",
    title: "Workshop Facilitator",
    church: "Kingdom Ambassadors Intl.",
    accent: "lilac",
  },
  {
    name: "Rev. Dr. Faith Akinola",
    title: "Session Speaker",
    church: "Grace Tabernacle",
    accent: "gold",
  },
  {
    name: "Evangelist Peter Obi",
    title: "Worship & Impartation",
    church: "Glory House Ministries",
    accent: "lilac",
  },
];

const SpeakersSection = () => {
  return (
    <section
      id="speakers"
      className="relative py-24 overflow-hidden"
      style={{ background: "linear-gradient(180deg, #2D0A4E 0%, #1A0533 50%, #2D0A4E 100%)" }}
    >
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/3 right-0 w-80 h-80 rounded-full bg-[#9B72AA]/5 blur-3xl" />
        <div className="absolute bottom-0 left-1/4 w-72 h-72 rounded-full bg-[#C9972A]/3 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-16">
          <p className="text-[#C9972A] text-xs sm:text-sm font-semibold tracking-widest uppercase mb-3">
            Kingdom Voices
          </p>
          <h2 className="text-3xl sm:text-5xl font-bold text-white mb-4">
            Featured Speakers
          </h2>
          <p className="text-white/60 max-w-xl mx-auto text-base sm:text-lg leading-relaxed">
            Anointed men and women of God gathered to pour fresh oil into your life and ministry.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
          {speakers.map((speaker, i) => (
            <div key={speaker.name} className="perspective-1000">
              <div
                className="rounded-2xl p-6 sm:p-8 text-center card-3d h-full"
                style={{
                  background: speaker.accent === "gold"
                    ? "linear-gradient(135deg, rgba(201, 151, 42, 0.08) 0%, rgba(45, 10, 78, 0.6) 50%, rgba(201, 151, 42, 0.04) 100%)"
                    : "linear-gradient(135deg, rgba(155, 114, 170, 0.15) 0%, rgba(45, 10, 78, 0.6) 50%, rgba(155, 114, 170, 0.08) 100%)",
                  border: speaker.accent === "gold"
                    ? "1px solid rgba(201, 151, 42, 0.2)"
                    : "1px solid rgba(155, 114, 170, 0.25)",
                }}
              >
                {/* Avatar placeholder */}
                <div className="relative mx-auto mb-5">
                  <div
                    className="w-20 h-20 sm:w-24 sm:h-24 rounded-full mx-auto flex items-center justify-center"
                    style={{
                      background: speaker.accent === "gold"
                        ? "linear-gradient(135deg, #C9972A, #2D0A4E, #C9972A)"
                        : "linear-gradient(135deg, #9B72AA, #2D0A4E, #9B72AA)",
                    }}
                  >
                    <Mic2 className="w-8 h-8 sm:w-10 sm:h-10 text-white/40" />
                  </div>
                  {/* Accent ring */}
                  <div
                    className="absolute inset-0 rounded-full animate-pulse-gold"
                    style={{
                      boxShadow: speaker.accent === "gold"
                        ? "0 0 20px rgba(201, 151, 42, 0.3)"
                        : "0 0 20px rgba(155, 114, 170, 0.3)",
                      animationDuration: "4s",
                      animationDelay: `${i * 0.5}s`,
                    }}
                  />
                </div>

                <h3 className="text-lg sm:text-xl font-bold text-white mb-1">
                  {speaker.name}
                </h3>
                <p className={speaker.accent === "gold" ? "gold-text text-sm font-semibold mb-1" : "lilac-text text-sm font-semibold mb-1"}>
                  {speaker.title}
                </p>
                <p className="text-white/45 text-xs sm:text-sm">
                  {speaker.church}
                </p>
              </div>
            </div>
          ))}
        </div>

        <p className="text-center text-white/30 text-xs mt-10 italic">
          More speakers to be announced…
        </p>
      </div>
    </section>
  );
};

export default SpeakersSection;