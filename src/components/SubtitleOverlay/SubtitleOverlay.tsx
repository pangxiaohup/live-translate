export default function SubtitleOverlay() {
  return (
    <div className="h-full w-full flex items-end justify-center pb-8 px-8 pointer-events-none">
      <div
        className="pointer-events-auto px-6 py-3 rounded-xl text-white text-2xl font-bold text-center max-w-3xl subtitle-text animate-slide-up"
        style={{ backgroundColor: 'rgba(0,0,0,0.75)' }}
      >
        <p className="text-sm text-gray-400 mb-1">🔍 原文 (中文) · 延迟 4.8s</p>
        <p>大家好欢迎来到我的直播间！</p>
        <p className="text-primary-300 mt-2 text-lg">
          Hello everyone, welcome to my livestream!
        </p>
      </div>
    </div>
  )
}
