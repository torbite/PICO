export async function sendPrompt(prompt: string) {
    try {
        const anyWindow = window as any
        if (anyWindow?.pico?.send) {
          const text: string = await anyWindow.pico.send(prompt)
          return text ?? '(sem resposta)'
        }
      } catch (e){
        return "No answer. ERROR: " + e
      }
}