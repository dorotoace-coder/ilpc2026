import { useState, useEffect } from "react";

const TARGET_DATE = new Date("2026-06-05T09:00:00").getTime();

interface TimeLeft {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
}

const CountdownTimer = () => {
  const [timeLeft, setTimeLeft] = useState<TimeLeft>({ days: 0, hours: 0, minutes: 0, seconds: 0 });

  useEffect(() => {
    const calc = () => {
      const diff = TARGET_DATE - Date.now();
      if (diff <= 0) return { days: 0, hours: 0, minutes: 0, seconds: 0 };
      return {
        days: Math.floor(diff / (1000 * 60 * 60 * 24)),
        hours: Math.floor((diff / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((diff / (1000 * 60)) % 60),
        seconds: Math.floor((diff / 1000) % 60),
      };
    };

    setTimeLeft(calc());
    const interval = setInterval(() => setTimeLeft(calc()), 1000);
    return () => clearInterval(interval);
  }, []);

  const units = [
    { label: "Days", value: timeLeft.days },
    { label: "Hours", value: timeLeft.hours },
    { label: "Minutes", value: timeLeft.minutes },
    { label: "Seconds", value: timeLeft.seconds },
  ];

  return (
    <div className="flex gap-3 sm:gap-5 justify-center">
      {units.map((unit) => (
        <div
          key={unit.label}
          className="perspective-1000"
        >
          <div className="glass rounded-xl p-3 sm:p-5 min-w-[70px] sm:min-w-[90px] text-center card-3d">
            <div className="text-2xl sm:text-4xl font-bold gold-text tabular-nums">
              {String(unit.value).padStart(2, "0")}
            </div>
            <div className="text-[10px] sm:text-xs text-white/60 mt-1 uppercase tracking-widest font-medium">
              {unit.label}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CountdownTimer;