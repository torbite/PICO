import React, { useState } from 'react'

export type Props = { onSend: (t: string) => void }

export default function InputBar({ onSend }: Props) {
  const [text, setText] = useState('')
  const send = () => {
    const t = text.trim()
    if (!t) return
    setText('')
    onSend(t)
  }
  return (
    <div className="inputBar">
      <textarea
        placeholder="Escreva para o PICO…"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button className="btn" onClick={send}>Enviar</button>
    </div>
  )
}