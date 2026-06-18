import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const STEPS = [
  { title: '欢迎', subtitle: 'Live Translate 设置向导' },
  { title: '硬件检测', subtitle: '检测系统配置' },
  { title: '模型下载', subtitle: '下载所需 AI 模型' },
  { title: '完成', subtitle: '一切就绪！' },
]

export default function SetupWizard() {
  const [step, setStep] = useState(0)
  const navigate = useNavigate()

  const handleFinish = () => {
    navigate('/')
  }

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
      <div className="w-full max-w-2xl mx-4">
        {/* Progress steps */}
        <div className="flex items-center justify-center mb-8">
          {STEPS.map((s, i) => (
            <div key={i} className="flex items-center">
              <div className={`
                w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold
                ${i < step ? 'bg-green-500 text-white' : ''}
                ${i === step ? 'bg-primary-500 text-white ring-4 ring-primary-200' : ''}
                ${i > step ? 'bg-gray-200 dark:bg-gray-700 text-gray-400' : ''}
              `}>
                {i < step ? '✓' : i + 1}
              </div>
              {i < STEPS.length - 1 && (
                <div className={`w-12 h-1 ${i < step ? 'bg-green-500' : 'bg-gray-200 dark:bg-gray-700'}`} />
              )}
            </div>
          ))}
        </div>

        {/* Step content */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-800">
          {/* Step 0: Welcome */}
          {step === 0 && (
            <div className="text-center">
              <div className="w-20 h-20 rounded-2xl bg-primary-500 flex items-center justify-center text-white text-3xl font-bold mx-auto mb-6">
                T
              </div>
              <h2 className="text-2xl font-bold mb-3">欢迎使用 Live Translate</h2>
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                实时直播 AI 翻译工具 — 支持任何直播平台<br />
                系统音频捕获 + 实时字幕叠加
              </p>
              <div className="text-left space-y-2 text-sm text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
                <p>✅ 自动捕获系统音频，无需额外配置</p>
                <p>✅ 本地 AI 模型，保护隐私</p>
                <p>✅ 支持 50+ 语言互译</p>
                <p>🔧 需下载模型文件（约 500MB-3GB）</p>
              </div>
            </div>
          )}

          {/* Step 1: Hardware Detection */}
          {step === 1 && (
            <div>
              <h2 className="text-xl font-bold mb-4">硬件检测</h2>
              <div className="space-y-3">
                <HardwareRow label="CPU" value="13th Gen Intel(R) Core(TM) i7-13700H" />
                <HardwareRow label="内存" value="16 GB" />
                <HardwareRow label="GPU" value="NVIDIA GeForce RTX 4060 (8GB VRAM)" />
                <HardwareRow label="CUDA" value="12.4 — 可用 ✅" />
                <HardwareRow label="磁盘空间" value="156 GB 可用" />
                <HardwareRow label="推荐模型" value="faster-whisper medium" badge="green" />
                <HardwareRow label="预计延迟" value="~3.2 秒" badge="blue" />
              </div>
            </div>
          )}

          {/* Step 2: Model Download */}
          {step === 2 && (
            <div>
              <h2 className="text-xl font-bold mb-4">模型下载</h2>
              <div className="space-y-4">
                <DownloadItem name="silero-vad" size="2 MB" progress={100} status="done" />
                <DownloadItem name="faster-whisper medium" size="1.5 GB" progress={0} status="pending" />
                <DownloadItem name="LibreTranslate 模型包" size="800 MB" progress={0} status="pending" />
              </div>
            </div>
          )}

          {/* Step 3: Complete */}
          {step === 3 && (
            <div className="text-center">
              <div className="w-20 h-20 rounded-full bg-green-500 flex items-center justify-center mx-auto mb-6">
                <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold mb-3">一切就绪！</h2>
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                模型下载完成，可以开始使用 Live Translate 了
              </p>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <button
            onClick={() => setStep(Math.max(0, step - 1))}
            disabled={step === 0}
            className="px-6 py-2 rounded-lg text-sm font-medium border border-gray-300 dark:border-gray-600 disabled:opacity-30 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            上一步
          </button>
          {step < STEPS.length - 1 ? (
            <button
              onClick={() => setStep(step + 1)}
              className="px-6 py-2 rounded-lg text-sm font-medium bg-primary-500 text-white hover:bg-primary-600 transition-colors"
            >
              下一步
            </button>
          ) : (
            <button
              onClick={handleFinish}
              className="px-6 py-2 rounded-lg text-sm font-medium bg-green-500 text-white hover:bg-green-600 transition-colors"
            >
              开始使用
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function HardwareRow({ label, value, badge }: { label: string; value: string; badge?: string }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
      <span className="text-sm text-gray-500">{label}</span>
      <span className={`text-sm font-medium flex items-center gap-2
        ${badge === 'green' ? 'text-green-600' : ''}
        ${badge === 'blue' ? 'text-blue-600' : ''}
      `}>
        {badge === 'green' && '✅ '}
        {value}
      </span>
    </div>
  )
}

function DownloadItem({ name, size, progress, status }: {
  name: string; size: string; progress: number; status: 'done' | 'pending' | 'downloading'
}) {
  return (
    <div className="flex items-center gap-4 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex-1">
        <p className="font-medium text-sm">{name}</p>
        <p className="text-xs text-gray-400">{size}</p>
      </div>
      <div className="flex items-center gap-3">
        {status === 'done' && <span className="text-green-500 text-sm font-medium">✅ 完成</span>}
        {status === 'pending' && (
          <button className="px-3 py-1 rounded-lg bg-primary-500 text-white text-xs font-medium hover:bg-primary-600 transition-colors">
            下载
          </button>
        )}
        {status === 'downloading' && (
          <div className="w-24 h-2 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
            <div className="h-full bg-primary-500 rounded-full transition-all" style={{ width: `${progress}%` }} />
          </div>
        )}
      </div>
    </div>
  )
}
