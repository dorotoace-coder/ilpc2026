import { MapPin, Navigation, Building2 } from "lucide-react";

const VenueSection = () => {
  return (
    <section
      className="relative py-24 overflow-hidden"
      style={{ background: "linear-gradient(180deg, #2D0A4E 0%, #1A0533 100%)" }}
    >
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 right-0 w-80 h-80 rounded-full bg-[#C9972A]/4 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <p className="text-[#C9972A] text-xs sm:text-sm font-semibold tracking-widest uppercase mb-3">
            The Venue
          </p>
          <h2 className="text-3xl sm:text-5xl font-bold text-white mb-4">
            Where We Gather
          </h2>
        </div>

        <div className="perspective-1000">
          <div
            className="rounded-2xl overflow-hidden card-3d"
            style={{
              background: "linear-gradient(135deg, rgba(155, 114, 170, 0.12) 0%, rgba(45, 10, 78, 0.6) 50%, rgba(201, 151, 42, 0.06) 100%)",
              border: "1px solid rgba(155, 114, 170, 0.2)",
            }}
          >
            <div className="grid grid-cols-1 md:grid-cols-2">
              {/* Map placeholder */}
              <div
                className="relative min-h-[250px] sm:min-h-[320px] flex items-center justify-center"
                style={{
                  background: "linear-gradient(135deg, #1A0533, #2D0A4E, #1A0533)",
                }}
              >
                {/* Grid pattern */}
                <div className="absolute inset-0 opacity-10" style={{
                  backgroundImage: "linear-gradient(rgba(201,151,42,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(201,151,42,0.3) 1px, transparent 1px)",
                  backgroundSize: "40px 40px",
                }} />
                <div className="relative text-center z-10">
                  <div className="w-16 h-16 rounded-full gold-gradient flex items-center justify-center mx-auto mb-4 animate-pulse-gold">
                    <MapPin className="w-8 h-8 text-[#2D0A4E]" />
                  </div>
                  <p className="text-white font-bold text-lg">HBG Ministry</p>
                  <p className="text-[#B88FC7] text-sm">Akute, Ogun State</p>
                  <a
                    href="https://maps.google.com/?q=Akute+Ogun+State+Nigeria"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 mt-4 text-[#C9972A] text-xs font-semibold tracking-wider uppercase hover:text-[#E8C547] transition-colors"
                  >
                    <Navigation className="w-3.5 h-3.5" />
                    Open in Maps
                  </a>
                </div>
              </div>

              {/* Venue details */}
              <div className="p-6 sm:p-8 flex flex-col justify-center">
                <div className="flex items-center gap-3 mb-5">
                  <div className="w-10 h-10 rounded-xl gold-gradient flex items-center justify-center">
                    <Building2 className="w-5 h-5 text-[#2D0A4E]" />
                  </div>
                  <div>
                    <h3 className="text-white font-bold text-lg">HBG Ministry International</h3>
                    <p className="text-[#B88FC7] text-xs">Conference Venue</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex gap-3 items-start">
                    <MapPin className="w-4 h-4 text-[#C9972A] mt-0.5 shrink-0" />
                    <div>
                      <p className="text-white/70 text-sm">Akute, Ogun State, Nigeria</p>
                      <p className="text-white/40 text-xs">Near Akute Roundabout, off Lagos-Abeokuta Expressway</p>
                    </div>
                  </div>

                  <div className="flex gap-3 items-start">
                    <Navigation className="w-4 h-4 text-[#C9972A] mt-0.5 shrink-0" />
                    <div>
                      <p className="text-white/70 text-sm">30 minutes from Ikeja, Lagos</p>
                      <p className="text-white/40 text-xs">Accessible via public transport and ride-hailing apps</p>
                    </div>
                  </div>

                  <div className="flex gap-3 items-start">
                    <Building2 className="w-4 h-4 text-[#C9972A] mt-0.5 shrink-0" />
                    <div>
                      <p className="text-white/70 text-sm">Spacious auditorium with seating for thousands</p>
                      <p className="text-white/40 text-xs">Parking, childcare, and refreshments available</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-4 rounded-xl" style={{
                  background: "rgba(155, 114, 170, 0.1)",
                  border: "1px solid rgba(155, 114, 170, 0.15)",
                }}>
                  <p className="text-[#B88FC7] text-xs leading-relaxed">
                    <span className="text-[#C9972A] font-semibold">Need directions?</span> Contact us on WhatsApp for step-by-step guidance to the venue.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default VenueSection;