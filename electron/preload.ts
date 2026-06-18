import { contextBridge, ipcRenderer } from 'electron'

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getPlatform: () => ipcRenderer.invoke('get-platform'),

  // Overlay
  toggleOverlay: () => ipcRenderer.invoke('toggle-overlay'),

  // Window
  setAlwaysOnTop: (flag: boolean) => ipcRenderer.invoke('set-always-on-top', flag),

  // Generic IPC
  send: (channel: string, ...args: unknown[]) => {
    const validChannels = ['toMain']
    if (validChannels.includes(channel)) {
      ipcRenderer.send(channel, ...args)
    }
  },
  receive: (channel: string, func: (...args: unknown[]) => void) => {
    const validChannels = ['fromMain', 'transcript-update', 'pipeline-status']
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, (_event, ...args) => func(...args))
    }
  },
  removeListener: (channel: string, func: (...args: unknown[]) => void) => {
    ipcRenderer.removeListener(channel, func)
  }
})

// Type declaration for renderer
declare global {
  interface Window {
    electronAPI: {
      getAppVersion: () => Promise<string>
      getPlatform: () => Promise<string>
      toggleOverlay: () => Promise<boolean>
      setAlwaysOnTop: (flag: boolean) => Promise<void>
      send: (channel: string, ...args: unknown[]) => void
      receive: (channel: string, func: (...args: unknown[]) => void) => void
      removeListener: (channel: string, func: (...args: unknown[]) => void) => void
    }
  }
}
