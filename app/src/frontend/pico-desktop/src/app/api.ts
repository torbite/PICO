import { Config } from './config'

// simple, typed auth header helper
function authHeaders(): Record<string, string> {
  const t = localStorage.getItem('auth_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

export async function signIn(email: string, code: string) {
  const res = await fetch(`${Config.API_BASE}/auth/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' } as HeadersInit,
    body: JSON.stringify({ email, code })
  })
  if (!res.ok) throw new Error('Auth failed')
  const json = await res.json()
  localStorage.setItem('auth_token', json.token)
}

export async function checkSubscription() {
  const res = await fetch(`${Config.API_BASE}/subscription/status`, {
    headers: authHeaders() as HeadersInit
  })
  if (!res.ok) return { active: false }
  return res.json() as Promise<{ active: boolean; plan?: string }>
}

export async function sendPrompt(prompt: string) {

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...authHeaders()
  }
  const res = await fetch(`${Config.API_BASE}/pico/prompt`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ prompt })
  })
  const data = await res.json()
  return data ?? '(sem resposta)'
}