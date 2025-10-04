export default function DungeonPage() {
  const remoteUrl = "https://o4s8sossskck88cwos0kw88o.a.selfhosted.hackclub.com";

  return (
    <div className="p-8 sm:p-20 min-h-screen bg-[#1E1E1E] flex items-center justify-center">
      {/* macOS Terminal Window */}
      <div className="w-full max-w-6xl bg-black rounded-lg overflow-hidden shadow-2xl">
        {/* Terminal Title Bar */}
        <div className="bg-[#2D2D2D] px-4 py-2 flex items-center gap-2 border-b border-[#404040]">
          <div className="flex gap-2">
            <div className="w-3 h-3 rounded-full bg-[#FF5F56] flex items-center justify-center">
              <div className="w-2.5 h-2.5 rounded-full bg-[#FF5F56] shadow-inner"></div>
            </div>
            <div className="w-3 h-3 rounded-full bg-[#FFBD2E] flex items-center justify-center">
              <div className="w-2.5 h-2.5 rounded-full bg-[#FFBD2E] shadow-inner"></div>
            </div>
            <div className="w-3 h-3 rounded-full bg-[#27C93F] flex items-center justify-center">
              <div className="w-2.5 h-2.5 rounded-full bg-[#27C93F] shadow-inner"></div>
            </div>
          </div>
          <div className="flex-1 text-center text-sm text-[#808080] font-medium">remote@hackclub — dungeon</div>
        </div>

        {/* Terminal Content (Iframe) */}
        <div className="bg-black" style={{ height: "70vh" }}>
          <iframe
            src={remoteUrl}
            title="Dungeon Terminal"
            className="w-full h-full"
            frameBorder={0}
            allowFullScreen
            referrerPolicy="no-referrer"
          />
        </div>
      </div>
    </div>
  );
}


