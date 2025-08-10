import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { signIn } from '../app/api'

export default function SignInScreen() {
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)

  const doSignIn = async () => {
    try {
      setLoading(true)
      await signIn(email.trim(), code.trim())
      nav('/sub')
    } catch (e: any) {
      alert('Erro ao entrar: ' + (e?.message || ''))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ padding: 24 }}>
      <div className="card">
        <h1 className="title">PICO</h1>
        <div className="subtitle">
          Programa de Interação e Controle Operacional
        </div>

        <input
          className="input"
          placeholder="Seu e-mail"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="input"
          placeholder="Código de acesso"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          type="password"
        />

        <button
          className="btn"
          onClick={doSignIn}
          disabled={loading}
        >
          {loading ? 'Entrando…' : 'Entrar'}
        </button>

        {/* Dev-only skip button */}
        {import.meta.env.DEV && (
          <button
            className="btn"
            style={{ marginTop: 10, background: '#555' }}
            onClick={() => nav('/chat')}
          >
            Pular login (teste)
          </button>
        )}
      </div>
    </div>
  )
}