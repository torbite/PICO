import React, { useRef, useState } from 'react'
import MessageBubble from '../components/MessageBubble'
import InputBar from '../components/InputBar'
import { sendPrompt } from '../app/api'

type Msg = { id:string; role:'user'|'assistant'; text:string; createdAt:number }

export default function ChatScreen(){
  const [messages,setMessages] = useState<Msg[]>([
    { id:'m1', role:'assistant', text:'Oi! Eu sou o PICO. O que você quer fazer?', createdAt:Date.now() }
  ])
  const listRef = useRef<HTMLDivElement>(null)

  const scrollToEnd = ()=>{ requestAnimationFrame(()=>{ listRef.current?.scrollTo(0, listRef.current.scrollHeight) }) }

  const onSend = async(text:string)=>{
    const user: Msg = { id:'u'+Date.now(), role:'user', text, createdAt:Date.now() }
    setMessages(m=>[...m,user]); scrollToEnd()
    try{
      const reply = await sendPrompt(text)
      const bot: Msg = { id:'a'+Date.now(), role:'assistant', text: reply, createdAt:Date.now() }
      setMessages(m=>[...m,bot]); scrollToEnd()
    }catch(e){
      setMessages(m=>[...m,{ id:'e'+Date.now(), role:'assistant', text:'Falha ao falar com o PICO.', createdAt:Date.now() }])
      scrollToEnd()
    }
  }

  return (
    <div className="container">
      <div className="header">
        <h1>PICO</h1>
        <div className="sub">Online</div>
      </div>
      <div className="messages" ref={listRef}>
        {messages.map(m=> <MessageBubble key={m.id} text={m.text} mine={m.role==='user'} />)}
      </div>
      <InputBar onSend={onSend} />
    </div>
  )
}