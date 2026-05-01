import { Music, Headphones, Disc3 } from "lucide-react";

const SpotifySection = () => {
  return (
    <div className="w-full max-w-lg mx-auto mb-10">
      <div className="text-center mb-5">
        <p className="text-[#C9972A] text-xs font-semibold tracking-widest uppercase mb-3">
          Listen Before You Come
        </p>
        <h3 className="text-2xl sm:text-3xl font-bold text-white mb-2">
          Tune Your Spirit
        </h3>
        <p className="text-white/50 text-sm">
          Get ready for ILPC 2026 with worship, teachings & more
        </p>
      </div>

      <div
        className="rounded-2xl overflow-hidden card-3d"
        style={{
          background: "linear-gradient(135deg, rgba(155, 114, 170, 0.25) 0%, rgba(45, 10, 78, 0.7) 50%, rgba(155, 114, 170, 0.15) 100%)",
          border: "1px solid rgba(155, 114, 170, 0.3)",
        }}
      >
        {/* Spotify Header Bar */}
        <div
          className="flex items-center justify-between px-5 py-3"
          style={{ background: "rgba(155, 114, 170, 0.15)" }}
        >
          <div className="flex items-center gap-2">
            <Disc3 className="w-5 h-5 text-[#1DB954] animate-spin" style={{ animationDuration: "3s" }} />
            <span className="text-[#B88FC7] text-xs font-bold tracking-wider uppercase">
              Spotify
            </span>
          </div>
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-[#1DB954]/60" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#C9972A]/60" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#9B72AA]/60" />
          </div>
        </div>

        {/* Player Placeholder */}
        <div className="p-6 sm:p-8 text-center">
          <div className="relative mb-6">
            {/* Album art placeholder */}
            <div
              className="w-28 h-28 sm:w-32 sm:h-32 rounded-2xl mx-auto flex items-center justify-center relative overflow-hidden"
              style={{
                background: "linear-gradient(135deg, #9B72AA 0%, #2D0A4E 50%, #C9972A 100%)",
              }}
            >
              <Music className="w-12 h-12 sm:w-14 sm:h-14 text-white/30" />
              {/* Shimmer overlay */}
              <div
                className="absolute inset-0 animate-shimmer opacity-20"
                style={{
                  background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)",
                  backgroundSize: "200% auto",
                }}
              />
            </div>
            {/* Floating headphones icon */}
            <div className="absolute -bottom-2 -right-2 sm:right-4 w-10 h-10 rounded-full gold-gradient flex items-center justify-center shadow-lg">
              <Headphones className="w-5 h-5 text-[#2D0A4E]" />
            </div>
          </div>

          {/* Track info placeholder */}
          <p className="text-white font-bold text-base mb-1">
            ILPC 2026 — Fresh Oil
          </p>
          <p className="text-[#B88FC7] text-xs font-medium tracking-wider uppercase mb-5">
            Conference Playlist
          </p>

          {/* Fake progress bar */}
          <div className="w-full h-1 rounded-full bg-white/10 mb-2 overflow-hidden">
            <div
              className="h-full rounded-full animate-shimmer"
              style={{
                width: "35%",
                background: "linear-gradient(90deg, #9B72AA, #C9972A, #9B72AA)",
                backgroundSize: "200% auto",
              }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-white/30 mb-5">
            <span>0:00</span>
            <span>Coming Soon</span>
          </div>

          {/* Playback controls placeholder */}
          <div className="flex items-center justify-center gap-6 mb-5">
            <div className="w-8 h-8 rounded-full border border-[#9B72AA]/40 flex items-center justify-center text-[#B88FC7] hover:border-[#C9972A] hover:text-[#C9972A] transition-colors cursor-pointer">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><rect x="0" y="1" width="3" height="10" rx="1"/><rect x="5" y="1" width="3" height="10" rx="1"/></svg>
            </div>
            <div className="w-12 h-12 rounded-full gold-gradient flex items-center justify-center text-[#2D0A4E] hover:scale-110 transition-transform cursor-pointer shadow-lg shadow-[#C9972A]/20">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><polygon points="3,1 13,8 3,15"/></svg>
            </div>
            <div className="w-8 h-8 rounded-full border border-[#9B72AA]/40 flex items-center justify-center text-[#B88FC7] hover:border-[#C9972A] hover:text-[#C9972A] transition-colors cursor-pointer">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><rect x="0" y="1" width="3" height="10" rx="1"/><rect x="5" y="1" width="3" height="10" rx="1"/></svg>
            </div>
          </div>

          {/* Coming soon note */}
          <div
            className="rounded-xl px-4 py-3 text-center"
            style={{
              background: "rgba(155, 114, 170, 0.12)",
              border: "1px solid rgba(155, 114, 170, 0.2)",
            }}
          >
            <p className="text-[#B88FC7] text-xs sm:text-sm leading-relaxed font-medium">
              Conference talks, worship and the ILPC jingle coming soon on Spotify
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpotifySection;