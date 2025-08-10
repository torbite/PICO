import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { checkSubscription } from '../app/api'

export default function SubscriptionGate(){
  const nav = useNavigate()
  const [loading,setLoading] = useState(true)
  const [active,setActive] = useState(false)
  const [plan,setPlan] = useState<string|undefined>()

  useEffect(()=>{(async()=>{ const s = await checkSubscription(); setActive(s.active); setPlan(s.plan); setLoading(false) })()},[])

  if(loading) return <div className="container" style={{placeItems:'center', display:'grid'}}>Checando assinatura…</div>

  
  if(!active) return (
    <div className="container" style={{ padding: 24 }}>
    <div className="card">
      <h2 style={{ marginTop: 0 }}>Assinatura necessária</h2>
      <p className="subtitle">
        Para usar o PICO, ative sua assinatura. (Checkout aqui.)
      </p>
      <button className="btn" onClick={() => alert('TODO: Checkout')}>
        Ativar agora
      </button>

      {/* TEST SKIP BUTTON */}
      <button
        className="btn"
        style={{ marginTop: 10, background: '#555' }}
        onClick={() => nav('/chat')}
      >
        Pular (teste)
      </button>
    </div>
  </div>
  )

  return (
    <div className="container" style={{placeItems:'center', display:'grid'}}>
      <div>
        <div className="subtitle" style={{marginBottom:12}}>Plano: {plan||'ativo'}</div>
        <button className="btn" onClick={()=>nav('/chat')}>Entrar no chat</button>
      </div>
    </div>
  )
}