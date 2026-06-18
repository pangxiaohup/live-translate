import { useState } from 'react'

export default function ControlPanel() {
  const [streamUrl, setStreamUrl] = useState('')
  const [isTranslating, setIsTranslating] = useState(false)
  const [sourceLang, setSourceLang] = useState('auto')
  const [targetLang, setTargetLang] = useState('zh')

  const handleStartStop = () => {
    setIsTranslating(!isTranslating)
  }

  return (
    <div className="h-full flex flex-col p-6 overflow-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold">实时翻译</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          系统音频捕获 — 支持任何直播平台
        </p>
      </div>

      {/* Audio source indicator */}
      <div className="mb-6 p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
          <div>
            <p className="font-medium text-green-800 dark:text-green-200">
              🎧 系统音频捕获就绪
            </p>
            <p className="text-xs text-green-600 dark:text-green-400 mt-0.5">
              自动捕获系统音频输出 — 无需额外配置
            </p>
          </div>
        </div>
      </div>

      {/* Stream URL (experimental) */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">
          直播直连 URL
          <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400">
            🧪 实验模式
          </span>
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={streamUrl}
            onChange={(e) => setStreamUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=... 或 Twitch URL"
            className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
          />
        </div>
        <p className="text-xs text-gray-400 mt-1">
          留空则使用系统音频捕获（推荐）
        </p>
      </div>

      {/* Language selection */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-2">源语言</label>
          <select
            value={sourceLang}
            onChange={(e) => setSourceLang(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            <option value="auto">🔍 自动检测</option>
            <option value="zh">中文</option>
            <option value="en">English</option>
            <option value="ja">日本語</option>
            <option value="ko">한국어</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">目标语言</label>
          <select
            value={targetLang}
            onChange={(e) => setTargetLang(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            <option value="zh">中文</option>
            <option value="en">English</option>
            <option value="ja">日本語</option>
            <option value="ko">한국어</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
          </select>
        </div>
      </div>

      {/* Delay control */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">
          延迟：<span className="text-primary-500 font-bold">5 秒</span>
        </label>
        <input
          type="range"
          min="3"
          max="15"
          defaultValue="5"
          className="w-full h-2 rounded-full bg-gray-200 dark:bg-gray-700 appearance-none cursor-pointer accent-primary-500"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>3s (低延迟)</span>
          <span>15s (高精度)</span>
        </div>
      </div>

      {/* Start/Stop button */}
      <button
        onClick={handleStartStop}
        className={`w-full py-3 rounded-xl font-semibold text-white transition-all duration-300 shadow-lg
          ${isTranslating
            ? 'bg-red-500 hover:bg-red-600 shadow-red-500/30'
            : 'bg-primary-500 hover:bg-primary-600 shadow-primary-500/30'
          }`}
      >
        {isTranslating ? '⏹ 停止翻译' : '▶ 开始翻译'}
      </button>

      {/* Status */}
      {isTranslating && (
        <div className="mt-4 p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 animate-slide-up">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm font-medium">翻译运行中...</span>
            <span className="text-xs text-gray-400 ml-auto">延迟 4.8s</span>
          </div>
          <div className="text-xs text-gray-400 space-y-0.5">
            <p>源语言：自动检测 → 中文（置信度 92%）</p>
            <p>目标语言：English</p>
            <p>缓冲：6.2s / 10s | STT：faster-whisper small</p>
          </div>
        </div>
      )}
    </div>
  )
}
