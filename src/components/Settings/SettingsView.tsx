export default function SettingsView() {
  return (
    <div className="h-full flex flex-col p-6 overflow-auto">
      <h1 className="text-2xl font-bold mb-6">设置</h1>

      {/* Translation Settings */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4">翻译引擎</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
            <div>
              <p className="font-medium">LibreTranslate (本地)</p>
              <p className="text-xs text-gray-400">离线翻译，50+ 语言 | 状态：未下载</p>
            </div>
            <input type="checkbox" defaultChecked className="toggle" />
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
            <div>
              <p className="font-medium">DeepL API</p>
              <p className="text-xs text-gray-400">更高质量翻译 | 需要 API Key</p>
            </div>
            <input type="checkbox" className="toggle" />
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
            <div>
              <p className="font-medium">GPT-4o-mini</p>
              <p className="text-xs text-gray-400">上下文感知翻译 | 需要 API Key</p>
            </div>
            <input type="checkbox" className="toggle" />
          </div>
        </div>
      </section>

      {/* Subtitle Style */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4">字幕样式</h2>
        <div className="grid grid-cols-4 gap-3">
          {['经典', '半透明', '极简', '电竞'].map((theme) => (
            <button
              key={theme}
              className="p-3 rounded-lg border-2 border-gray-200 dark:border-gray-700 hover:border-primary-500 transition-colors text-sm"
            >
              {theme}
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}
