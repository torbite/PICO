import React from 'react'

type Props = { text: string; mine?: boolean }
export default function MessageBubble({ text, mine }: Props){
  return (
    <div className={`row ${mine? 'mine':'other'}`}>
      <div className={`bubble ${mine? 'mine':'other'}`}>{text}</div>
    </div>
  )
}