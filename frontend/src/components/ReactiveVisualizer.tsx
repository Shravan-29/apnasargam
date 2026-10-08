import { useEffect, useRef } from 'react'

interface NoteBar {
  hue: number
  intensity: number
}

export default function ReactiveVisualizer({ playerRef }: { playerRef: React.RefObject<HTMLElement> }) {
  const wrapRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const barsRef = useRef<NoteBar[]>(Array.from({ length: 32 }, () => ({ hue: 0, intensity: 0 })))

  useEffect(() => {
    const playerEl = playerRef.current
    if (!playerEl) return

    const handleNote = (e: Event) => {
      const custom = e as CustomEvent
      const pitch = custom.detail?.note?.midi ?? 60
      const barIndex = pitch % barsRef.current.length
      const hue = ((pitch - 40) / 48) * 280
      barsRef.current[barIndex] = { hue, intensity: 1 }
    }

    playerEl.addEventListener('note', handleNote)
    return () => playerEl.removeEventListener('note', handleNote)
  }, [playerRef])

  // Canvas resolution matches the wrapper's actual rendered width, kept
  // in sync via ResizeObserver. Without this, a fixed canvas width looks
  // stretched or cramped at narrower viewport widths (phones, tablets).
  useEffect(() => {
    const wrap = wrapRef.current
    const canvas = canvasRef.current
    if (!wrap || !canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resize = () => {
      const rect = wrap.getBoundingClientRect()
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      canvas.width = rect.width * dpr
      canvas.height = 80 * dpr
      canvas.style.width = `${rect.width}px`
      canvas.style.height = '80px'
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    }
    resize()

    const observer = new ResizeObserver(resize)
    observer.observe(wrap)

    let frameId: number
    const draw = () => {
      frameId = requestAnimationFrame(draw)
      const width = wrap.getBoundingClientRect().width
      ctx.clearRect(0, 0, width, 80)

      const barWidth = width / barsRef.current.length
      barsRef.current.forEach((bar, i) => {
        bar.intensity *= 0.92
        const height = bar.intensity * 80
        ctx.fillStyle = `hsl(${bar.hue}, 80%, 60%)`
        ctx.shadowColor = `hsl(${bar.hue}, 80%, 60%)`
        ctx.shadowBlur = bar.intensity * 12
        ctx.fillRect(i * barWidth + 2, 80 - height, Math.max(barWidth - 4, 1), height)
      })
    }
    draw()

    return () => {
      cancelAnimationFrame(frameId)
      observer.disconnect()
    }
  }, [])

  return (
    <div ref={wrapRef} className="w-full">
      <canvas ref={canvasRef} className="rounded-lg bg-bg block" />
    </div>
  )
}
