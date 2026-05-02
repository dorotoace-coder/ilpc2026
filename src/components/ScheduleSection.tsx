import { Calendar, Clock, MapPin } from "lucide-react";

const schedule = [
  {
    day: "Day 1",
    date: "Friday, June 5",
    title: "Arrival & Ablaze for Christ",
    events: [
      { time: "5:00 PM", session: "Registration & Accreditation" },
      { time: "6:00 PM", session: "Leadership Masterclass — Ablaze for Christ" },
    ],
  },
  {
    day: "Day 2",
    date: "Saturday, June 6",
    title: "Equipping & Supernatural Encounter",
    events: [
      { time: "8:00 AM", session: "Registration & Accreditation" },
      { time: "9:30 AM", session: "Session 1 — Fresh Oil for Ministry" },
      { time: "11:30 AM", session: "Session 2 — Navigating the New Season" },
      { time: "1:00 PM", session: "Lunch Break" },
      { time: "5:00 PM", session: "Night of Supernatural Encounter" },
    ],
  },
  {
    day: "Day 3",
    date: "Sunday, June 7",
    title: "Commissioning & Closing Service",
    events: [
      { time: "8:00 AM", session: "Morning Devotion" },
      { time: "9:30 AM", session: "Session 3 — Apostolic Commissioning" },
      { time: "11:00 AM", session: "Praise & Worship Service" },
      { time: "12:30 PM", session: "Communion & Covenant Meal" },
      { time: "2:00 PM", session: "Closing Remarks & Departure" },
    ],
  },
];

const ScheduleSection = () => {
  return (
    <section
      id="schedule"
      className="relative py-24 overflow-hidden"
      style={{ background: "linear-gradient(180deg, #1A0533 0%, #2D0A4E 50%, #1A0533 100%)" }}
    >
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-0 w-96 h-96 rounded-full bg-[#C9972A]/3 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-16">
          <p className="text-[#C9972A] text-xs sm:text-sm font-semibold tracking-widest uppercase mb-3">
            Conference Program
          </p>
          <h2 className="text-3xl sm:text-5xl font-bold text-white mb-4">
            3 Days of Encounter
          </h2>
          <div className="flex items-center justify-center gap-4 sm:gap-6 text-white/40 text-xs sm:text-sm mt-4">
            <span className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-[#C9972A]" /> June 5–7, 2026
            </span>
            <span className="flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-[#C9972A]" /> HBG Ministry, Akute
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
          {schedule.map((day, i) => (
            <div key={day.day} className="perspective-1000">
              <div className="glass rounded-2xl overflow-hidden card-3d h-full flex flex-col">
                {/* Day Header */}
                <div className="gold-gradient p-5 sm:p-6 text-center">
                  <p className="text-[#2D0A4E]/70 text-xs font-bold tracking-widest uppercase">
                    {day.day}
                  </p>
                  <h3 className="text-[#2D0A4E] text-lg sm:text-xl font-black">
                    {day.date}
                  </h3>
                </div>

                {/* Title */}
                <div className="px-5 sm:px-6 pt-5">
                  <h4 className="text-white font-bold text-base mb-4">
                    {day.title}
                  </h4>
                </div>

                {/* Events */}
                <div className="px-5 sm:px-6 pb-5 sm:pb-6 flex-1">
                  <div className="space-y-3">
                    {day.events.map((event) => (
                      <div key={event.time + event.session} className="flex gap-3 items-start">
                        <div className="flex items-center gap-1.5 shrink-0 mt-0.5">
                          <Clock className="w-3.5 h-3.5 text-[#C9972A]/70" />
                          <span className="text-[#C9972A] text-xs font-semibold whitespace-nowrap">
                            {event.time}
                          </span>
                        </div>
                        <p className="text-white/60 text-xs sm:text-sm leading-relaxed">
                          {event.session}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ScheduleSection;