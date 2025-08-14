/// <reference types="vite/client" />

interface Window {
  pico?: {
    version: string
    send: (prompt: string, opts?: { asSystem?: boolean; speak?: boolean }) => Promise<string>
  }
  ipcRenderer?: {
    on: (...args: any[]) => void
    off: (...args: any[]) => void
    send: (...args: any[]) => void
    invoke: (channel: string, ...args: any[]) => Promise<any>
  }
}