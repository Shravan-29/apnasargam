import { useEffect, useRef } from 'react'

interface NoteBar {
  hue: number
  intensity: number
}

export default function ReactiveVisualizer({ playerRef }: { playerRef: React.RefObject<HTMLElement> }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const barsRef = useRef<NoteBar[]>(Array.from({ length: 32 }, () => ({ hue: 0, intensity: 0 })))

  useEffect(() => {
    const playerEl = playerRef.current
    if (!playerEl) return

    // html-midi-player dispatches a 'note' CustomEvent for every note
    // that starts playing, with the MIDI pitch in event.detail.note.midi
    const handleNote = (e: Event) => {
      const custom = e as CustomEvent
      const pitch = custom.detail?.note?.midi ?? 60
      const barIndex = pitch % barsRef.current.length
      const hue = ((pitch - 40) / 48) * 280 // map pitch range to a hue spread (gold -> indigo -> pink)
      barsRef.current[barIndex] = { hue, intensity: 1 }
    }

    playerEl.addEventListener('note', handleNote)
    return () => playerEl.removeEventListener('note', handleNote)
  }, [playerRef])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let frameId: number
    const draw = () => {
      frameId = requestAnimationFrame(draw)
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      const barWidth = canvas.width / barsRef.current.length
      barsRef.current.forEach((bar, i) => {
        bar.intensity *= 0.92 // decay so bars fade out smoothly after a note ends
        const height = bar.intensity * canvas.height
        ctx.fillStyle = `hsl(${bar.hue}, 80%, 60%)`
        ctx.shadowColor = `hsl(${bar.hue}, 80%, 60%)`
        ctx.shadowBlur = bar.intensity * 12
        ctx.fillRect(i * barWidth + 2, canvas.height - height, barWidth - 4, height)
      })
    }
    draw()
    return () => cancelAnimationFrame(frameId)
  }, [])

  return <canvas ref={canvasRef} width={800} height={80} className="w-full rounded-lg bg-bg" />
}