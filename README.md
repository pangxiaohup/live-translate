# Live Translate

YouTube + Twitch 实时直播 AI 翻译桌面应用。

## 功能

- 🎧 系统音频捕获（默认）— 支持任何直播平台
- 🧠 实时语音转文字（STT）— 基于 faster-whisper
- 🌐 AI 多语言翻译 — 本地 LibreTranslate + 可选云端后端
- 📺 字幕悬浮窗 — 无边框透明叠加层
- 🇨🇳 中文错误恢复 — 同音字/上下文纠错
- 🎛️ 灵活延迟控制 — 3-15 秒可调

## 技术栈

| 层 | 技术 |
|---|------|
| 桌面框架 | Electron 31+ / React 18 / TypeScript |
| 后端 | Python 3.11 / FastAPI / WebSocket |
| STT | faster-whisper (CTranslate2) |
| 翻译 | LibreTranslate / DeepL / GPT-4o-mini |
| 音频 | WASAPI / CoreAudio / silero-vad |

## 开发状态

🚧 Phase 1 准备中 — 详见 [架构计划](docs/architecture.md)
