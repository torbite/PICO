import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { signIn } from '../app/api'

export default function SignInScreen() {
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [showCode, setShowCode] = useState(false)
  const [remember, setRemember] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const doSignIn = async () => {
    try {
      setLoading(true)
      setError(null)
      await signIn(email.trim(), code.trim())
      // (opcional) persistir email para lembrar depois
      if (remember) localStorage.setItem('pico_last_email', email.trim())
      nav('/sub')
    } catch (e: any) {
      setError(e?.message || 'Falha ao autenticar')
      alert('Erro ao entrar: ' + (e?.message || ''))
    } finally {
      setLoading(false)
    }
  }

  const demoFill = () => {
    setEmail('teste@pico.ai')
    setCode('123456')
  }

  return (
    <div className="bg-sky" style={{ minHeight: '100vh', position: 'relative' }}>
      {/* CLOUDS BACKGROUND */}
      <div
        className="cloud-layer"
        style={{
          position: 'absolute',
          inset: '-20vh -30vw',
          zIndex: 0,
          pointerEvents: 'none',
          overflow: 'hidden',
        }}
      >
        {[...Array(28)].map((_, i) => {
          const y = Math.random() * 100; // vh
          const w = 100 + Math.random() * 140; // px
          const speed = 40 + Math.random() * 70; // s
          const scale = 0.7 + Math.random() * 0.8;
          const opacity = 0.65 + Math.random() * 0.25;
          const shape = Math.floor(Math.random() * 3) + 1
          const delay = -Math.random() * speed;

          return (
            <div
              key={i}
              className={`cloud shape${shape}`}
              style={{
                position: 'absolute',
                top: `${y}vh`,
                width: `${w}px`,
                height: `${w * 0.45}px`,
                opacity,
                animation: `moveCloud ${speed}s linear infinite`,
                animationDelay: `${delay}s`,
                transform: `scale(${scale})`,
              }}
            />
          );
        })}
      </div>

      {/* FOREGROUND CONTENT */}
      <div
        style={{
          position: 'relative',
          zIndex: 1,
          display: 'grid',
          placeItems: 'center',
          minHeight: 'inherit',
          padding: 24,
        }}
      >
        <div className="card" style={{ width: '100%', maxWidth: 440 }}>
          {/* Header / Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: 12,
                display: 'grid',
                placeItems: 'center',
                background: 'var(--blue3)',
                color: 'white',
                fontWeight: 800,
              }}
            >
              P
            </div>
            <div>
              <h1 className="title" style={{ margin: 0 }}>
                PICO
              </h1>
              <div className="subtitle">
                Programa de Interação e Controle Operacional
              </div>
            </div>
          </div>

          {import.meta.env.DEV && (
            <div
              style={{
                fontSize: 12,
                color: 'var(--blue0)',
                background: 'var(--blue5)',
                padding: '4px 8px',
                borderRadius: 8,
                width: 'fit-content',
                marginBottom: 12,
              }}
            >
              Ambiente de desenvolvimento
            </div>
          )}

          {/* Email */}
          <label style={{ fontSize: 13, color: 'var(--sub)' }}>E-mail</label>
          <input
            className="input"
            placeholder="seu@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            inputMode="email"
          />
          <div
            className="subtitle"
            style={{ fontSize: 12, marginTop: -6, marginBottom: 6 }}
          >
            Use o e-mail associado à sua conta PICO.
          </div>

          {/* Código / Senha de acesso */}
          <label style={{ fontSize: 13, color: 'var(--sub)' }}>Código de acesso</label>
          <div style={{ position: 'relative' }}>
            <input
              className="input"
              placeholder="••••••"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              type={showCode ? 'text' : 'password'}
              autoComplete="one-time-code"
            />
            <button
              type="button"
              className="btn"
              onClick={() => setShowCode((s) => !s)}
              style={{
                position: 'absolute',
                right: 6,
                top: 6,
                padding: '6px 10px',
                background: 'var(--surface)',
              }}
            >
              {showCode ? 'Ocultar' : 'Mostrar'}
            </button>
          </div>

          {/* Lembrar + Ajuda */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 8,
              marginTop: 8,
            }}
          >
            <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
              />
              <span className="subtitle">Lembrar de mim</span>
            </label>
            <button
              type="button"
              className="link"
              style={{
                background: 'transparent',
                border: 0,
                cursor: 'pointer',
              }}
              onClick={() => alert('Envie um novo código pelo e-mail cadastrado.')}
            >
              Esqueci meu código
            </button>
          </div>

          {error && (
            <div
              style={{
                marginTop: 10,
                padding: '8px 10px',
                borderRadius: 10,
                border: '1px solid #F25F5C22',
                color: '#F25F5C',
              }}
            >
              {error}
            </div>
          )}

          {/* Ações */}
          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            <button
              className="btn"
              onClick={doSignIn}
              disabled={loading || !email || !code}
            >
              {loading ? 'Entrando…' : 'Entrar'}
            </button>

            {import.meta.env.DEV && (
              <>
                <button
                  className="btn"
                  style={{ background: '#555' }}
                  onClick={() => nav('/chat')}
                >
                  Pular (teste)
                </button>
                <button
                  className="btn"
                  style={{ background: 'var(--br2)', color: '#000' }}
                  onClick={demoFill}
                >
                  Preencher demo
                </button>
              </>
            )}
          </div>

          {/* Divider */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              margin: '16px 0',
              color: 'var(--sub)',
            }}
          >
            <div style={{ height: 1, background: 'var(--border)', flex: 1 }} />
            <span>ou</span>
            <div style={{ height: 1, background: 'var(--border)', flex: 1 }} />
          </div>

          {/* Links úteis */}
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <button
              className="link"
              style={{
                background: 'transparent',
                border: 0,
                padding: 0,
                cursor: 'pointer',
              }}
              onClick={() => alert('Fluxo de criar conta — em breve')}
            >
              Criar conta
            </button>
            <span style={{ color: 'var(--border)' }}>•</span>
            <button
              className="link"
              style={{
                background: 'transparent',
                border: 0,
                padding: 0,
                cursor: 'pointer',
              }}
              onClick={() => alert('Abrir Termos de Uso')}
            >
              Termos
            </button>
            <span style={{ color: 'var(--border)' }}>•</span>
            <button
              className="link"
              style={{
                background: 'transparent',
                border: 0,
                padding: 0,
                cursor: 'pointer',
              }}
              onClick={() => alert('Abrir Política de Privacidade')}
            >
              Privacidade
            </button>
          </div>

          <div className="subtitle" style={{ marginTop: 16, fontSize: 12 }}>
            v0.1.0 • Suporte: suporte@pico.ai
          </div>
        </div>
      </div>
    </div>
  )
}