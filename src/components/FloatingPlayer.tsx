import { useEffect, useRef, useState } from "react";
import { Pause, Play, Music2, X } from "lucide-react";

const FloatingPlayer = () => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [visible, setVisible] = useState(true);
  const [attempted, setAttempted] = useState(false);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || attempted) return;
    setAttempted(true);
    audio.volume = 0.5;
    audio.play().then(() => setPlaying(true)).catch(() => {
      // Autoplay blocked — user interaction required, player stays visible
    });
  }, [attempted]);

  const toggle = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) {
      audio.pause();
      setPlaying(false);
    } else {
      audio.play();
      setPlaying(true);
    }
  };

  if (!visible) return null;

  return (
    <>
      <audio ref={audioRef} src="/aku-te-nigeria.mp3" loop preload="auto" />
      <div
        className="fixed bottom-5 left-5 z-50 flex items-center gap-3 px-4 py-3 rounded-2xl shadow-2xl"
        style={{
          background: "rgba(45,10,78,0.92)",
          border: "1px solid rgba(201,151,42,0.35)",
          backdropFilter: "blur(12px)",
        }}
      >
        <div className="relative w-8 h-8 rounded-full gold-gradient flex items-center justify-center shrink-0">
          <Music2
            className="w-4 h-4 text-[#2D0A4E]"
            style={{ animation: playing ? "rotate-slow 3s linear infinite" : "none" }}
          />
        </div>

        <div className="leading-tight">
          <p className="text-white text-xs font-bold">Aku Te Nigeria</p>
          <p className="text-[#C9972A] text-[10px]">ILPC 2026 Anthem</p>
        </div>

        <button
          onClick={toggle}
          className="w-8 h-8 rounded-full bg-[#C9972A]/20 hover:bg-[#C9972A]/40 flex items-center justify-center transition-colors"
        >
          {playing
            ? <Pause className="w-3.5 h-3.5 text-[#C9972A]" />
            : <Play className="w-3.5 h-3.5 text-[#C9972A] translate-x-px" />
          }
        </button>

        <button
          onClick={() => { audioRef.current?.pause(); setVisible(false); }}
          className="w-6 h-6 rounded-full hover:bg-white/10 flex items-center justify-center transition-colors"
        >
          <X className="w-3 h-3 text-white/40" />
        </button>
      </div>
    </>
  );
};

export default FloatingPlayer;
