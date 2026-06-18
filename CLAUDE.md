# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Dev Commands

```bash
npm run dev          # Start Vite dev server (Electron + React HMR)
npm run build:vite   # Compile TypeScript + Vite build only (skip electron-builder)
npm run build        # Full production build + electron-builder packaging
npm run lint         # ESLint on .ts/.tsx files
npm run test         # Run vitest unit tests
```

**Python backend** (not yet wired to Electron main process in Phase 1):
```bash
cd backend && pip install -r requirements.txt
python main.py       # Starts FastAPI + WebSocket on 127.0.0.1:auto-port
```

## Architecture Overview

This is an **Electron + Python hybrid desktop app** for real-time live-stream AI translation.

### Process Model

```
Electron Main (Node/TS)          Electron Renderer (React/TS)
├─ WindowManager                 ├─ ControlPanel (/)
├─ PythonBackendManager          ├─ TranscriptView (/transcript)
│  └─ spawns Python child        ├─ SettingsView (/settings)
├─ AudioLoopback (Phase 3)       ├─ SubtitleOverlay (/overlay)
└─ Tray/Updater                  └─ SetupWizard (/setup)

          WebSocket (127.0.0.1:random)
                    │
Python Backend (FastAPI)
├─ pipeline/orchestrator.py   ← Central coordinator
├─ pipeline/websocket_handler.py
├─ audio_capture/             ← AbstractCaptureSource + RingBuffer
├─ stt/                       ← AbstractSTTEngine (faster-whisper)
├─ translation/               ← AbstractTranslationEngine (LibreTranslate/DeepL/GPT)
└─ utils/                     ← hardware_detect, logger, metrics, language_utils
```

**Communication path:** Renderer ←(IPC)→ Main ←(spawn/monitor)→ Python ←(WebSocket)→ Renderer (direct for transcripts)

### Key Design Decisions (from docs/architecture.md)

1. **System audio capture is the default** — captures any audio playing on the system (browser, any platform). Live stream URL direct-connect (yt-dlp/streamlink) is experimental mode.
2. **Python runs as a child process**, not embedded in Node — the entire ML ecosystem (faster-whisper, silero-vad, LibreTranslate) is Python-native. Main process manages Python lifecycle (spawn, heartbeat, restart).
3. **WebSocket for real-time data**, not Electron IPC — transcript/translation streaming goes direct from Python to Renderer via WebSocket on 127.0.0.1 to avoid IPC serialization overhead.
4. **Vite builds three targets** in one config: React renderer (`dist/`), Electron main (`dist-electron/main.js`), preload (`dist-electron/preload.js`).

### Frontend Architecture

- **HashRouter** with 4 routes: `/` (ControlPanel), `/transcript` (TranscriptView), `/settings` (SettingsView), `/overlay` (SubtitleOverlay). `/setup` renders full-screen without sidebar.
- **Sidebar** is a shared shell component; `/overlay` and `/setup` bypass it in `AppLayout`.
- **State management**: Zustand (stores not yet implemented — Phase 1 is UI skeleton only).
- **Styling**: TailwindCSS with `dark` class-based dark mode, custom `primary` color palette, `subtitle-text` utility for text-shadow outlines on transparent overlays.
- **IPC bridge**: `electron/preload.ts` exposes `window.electronAPI` via `contextBridge`. Renderer calls it for overlay toggle, app info, window control.

### Python Backend Architecture

- **PipelineOrchestrator** (`pipeline/orchestrator.py`): State machine: `IDLE → STARTING → RUNNING → PAUSED/STOPPING → ERROR/DEGRADED`. Main loop reads from `asyncio.Queue` of audio chunks. Orchestrator will wire together VAD → STT → SentenceSegmenter → TranslationQueue → WebSocket broadcast in Phase 2.
- **Abstract base classes**: `AbstractCaptureSource`, `AbstractSTTEngine`, `AbstractTranslationEngine` define the plugin interfaces. Each backend (faster-whisper, whisper-cpp, LibreTranslate, DeepL, GPT-4o-mini) implements one.
- **RingBuffer** (`audio_capture/ring_buffer.py`): Thread-safe circular buffer with configurable capacity (default 10s audio), high-watermark backpressure (drops oldest chunks at >80%).
- **WebSocket protocol**: JSON messages with `type` field (`transcript_update`, `translation_update`, `status`, `pong`). Two emission modes: `is_partial: true` (mid-sentence streaming) and `is_partial: false` (finalized sentence).
- **HardwareDetector** (`utils/hardware_detect.py`): Detects CPU/GPU/CUDA/disk → recommends model size (tiny/small/medium/large-v3) with estimated latency.

### Development Phases (from plan)

We just completed **Phase 1**: project scaffolding, skeleton UI, Python backend structure, hardware detection, setup wizard, logging/metrics.

**Phase 2** (next): System audio capture → VAD → STT → Translation, end-to-end pipeline.

**Phase 3**: Delay control, SubtitleQueue, Chinese error recovery.

**Phase 4**: Experimental direct-stream mode, proxy/weak-network, cloud backends.

**Phase 5**: UI polish, global hotkeys, tray, SRT export, i18n.

**Phase 6**: Testing, packaging (Windows + macOS signing), auto-update, release.

## Important Paths

| Purpose | Path |
|---------|------|
| Electron main entry | `electron/main.ts` |
| Preload (IPC bridge) | `electron/preload.ts` |
| Vite config (3 targets) | `vite.config.ts` |
| Python entry | `backend/main.py` |
| Pipeline orchestrator | `backend/pipeline/orchestrator.py` |
| WebSocket handler | `backend/pipeline/websocket_handler.py` |
| Architecture plan | `docs/architecture.md` |
| Python deps | `backend/requirements.txt` |

## File Naming Conventions

- Electron main process: `electron/*.ts` (compiled to `dist-electron/`)
- React components: `src/components/<Feature>/<Feature>.tsx`
- Python modules: `backend/<module>/` with `__init__.py` + `base.py` (abstract) + concrete implementations
- Shared utilities: `backend/utils/` (no nested subdirectories)
