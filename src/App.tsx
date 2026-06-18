import { useState, useEffect } from 'react'
import { HashRouter, Routes, Route, useLocation } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import ControlPanel from './components/ControlPanel/ControlPanel'
import SettingsView from './components/Settings/SettingsView'
import TranscriptView from './components/TranscriptView/TranscriptView'
import SetupWizard from './components/SetupWizard/SetupWizard'
import SubtitleOverlay from './components/SubtitleOverlay/SubtitleOverlay'

function AppLayout() {
  const location = useLocation()

  // Don't show sidebar on overlay or wizard
  if (location.pathname === '/overlay') {
    return <SubtitleOverlay />
  }
  if (location.pathname === '/setup') {
    return <SetupWizard />
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-hidden">
        <Routes>
          <Route path="/" element={<ControlPanel />} />
          <Route path="/transcript" element={<TranscriptView />} />
          <Route path="/settings" element={<SettingsView />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  const [darkMode, setDarkMode] = useState(() => {
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
  }, [darkMode])

  return (
    <HashRouter>
      <AppLayout />
    </HashRouter>
  )
}
