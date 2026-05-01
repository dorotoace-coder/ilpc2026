import { useRef, useState, useEffect } from "react";
import { Music, Headphones, Disc3, Play, Pause, Volume2 } from "lucide-react";

const SpotifySection = () => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [current, setCurrent] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const onTime = () => setCurrent(audio.currentTime);
    const onLoad = () => setDuration(audio.duration);
    const onEnd = () => setPlaying(false);
    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("loadedmetadata", onLoad);
    audio.addEventListener("ended", onEnd);
    return () => {
      audio.removeEventListener("timeupdate", onTime);
      audio.removeEventListener("loadedmetadata", onLoad);
      audio.removeEventListener("ended", onEnd);
    };
  }, []);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) {
      audio.pause();
    } else {
      audio.play();
    }
    setPlaying(!playing);
  };

  const seek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = Number(e.target.value);
    setCurrent(Number(e.target.value));
  };

  const changeVolume = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = Number(e.target.value);
    setVolume(v);
    if (audioRef.current) audioRef.current.volume = v;
  };

  const fmt = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  return (
    <div className="w-full max-w-lg mx-auto mb-10">
      <audio ref={audioRef} src="/aku-te-nigeria.mp3" preload="metadata" />

      <div className="text-center mb-5">
        <p className="text-[#C9972A] text-xs font-semibold tracking-widest uppercase mb-3">
          Listen Now
        </p>
        <h3 className="text-2xl sm:text-3xl font-bold text-white mb-2">
          Tune Your Spirit
        </h3>
        <p className="text-white/50 text-sm">
          The official ILPC 2026 anthem — Aku Te Nigeria
        </p>
      </div>

      <div
        className="rounded-2xl overflow-hidden card-3d"
        style={{
          background: "linear-gradient(135deg, rgba(155,114,170,0.25) 0%, rgba(45,10,78,0.7) 50%, rgba(155,114,170,0.15) 100%)",
          border: "1px solid rgba(155,114,170,0.3)",
        }}
      >
        {/* Header bar */}
        <div
          className="flex items-center justify-between px-5 py-3"
          style={{ background: "rgba(155,114,170,0.15)" }}
        >
          <div className="flex items-center gap-2">
            <Disc3
              className="w-5 h-5 text-[#1DB954]"
              style={{ animation: playing ? "rotate-slow 3s linear infinite" : "none" }}
            />
            <span className="text-[#B88FC7] text-xs font-bold tracking-wider uppercase">
              Now Playing
            </span>
          </div>
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-[#1DB954]/60" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#C9972A]/60" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#9B72AA]/60" />
          </div>
        </div>

        {/* Player body */}
        <div className="p-6 sm:p-8 text-center">
          {/* Album art */}
          <div className="relative mb-6">
            <div
              className="w-28 h-28 sm:w-32 sm:h-32 rounded-2xl mx-auto flex items-center justify-center relative overflow-hidden"
              style={{ background: "linear-gradient(135deg, #9B72AA 0%, #2D0A4E 50%, #C9972A 100%)" }}
            >
              <Music className="w-12 h-12 sm:w-14 sm:h-14 text-white/30" />
              {playing && (
                <div
                  className="absolute inset-0 animate-shimmer opacity-20"
                  style={{
                    background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)",
                    backgroundSize: "200% auto",
                  }}
                />
              )}
            </div>
            <div className="absolute -bottom-2 -right-2 sm:right-4 w-10 h-10 rounded-full gold-gradient flex items-center justify-center shadow-lg">
              <Headphones className="w-5 h-5 text-[#2D0A4E]" />
            </div>
          </div>

          {/* Track info */}
          <p className="text-white font-bold text-base mb-1">Aku Te Nigeria</p>
          <p className="text-[#B88FC7] text-xs font-medium tracking-wider uppercase mb-5">
            ILPC 2026 — Fresh Oil for a New Season
          </p>

          {/* Progress bar */}
          <div className="mb-1">
            <input
              type="range"
              min={0}
              max={duration || 0}
              value={current}
              onChange={seek}
              className="w-full h-1 rounded-full appearance-none cursor-pointer"
              style={{ accentColor: "#C9972A" }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-white/30 mb-5">
            <span>{fmt(current)}</span>
            <span>{duration ? fmt(duration) : "--:--"}</span>
          </div>

          {/* Play/pause */}
          <div className="flex items-center justify-center gap-6 mb-5">
            <button
              onClick={togglePlay}
              className="w-14 h-14 rounded-full gold-gradient flex items-center justify-center text-[#2D0A4E] hover:scale-110 transition-transform shadow-lg shadow-[#C9972A]/20"
            >
              {playing ? <Pause size={22} /> : <Play size={22} className="translate-x-0.5" />}
            </button>
          </div>

          {/* Volume */}
          <div className="flex items-center gap-3 justify-center">
            <Volume2 className="w-4 h-4 text-[#B88FC7]" />
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={volume}
              onChange={changeVolume}
              className="w-28 h-1 rounded-full appearance-none cursor-pointer"
              style={{ accentColor: "#C9972A" }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpotifySection;
