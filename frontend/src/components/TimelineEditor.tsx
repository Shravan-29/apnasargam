import { useEffect, useRef, useState } from 'react'
import { Midi } from '@tonejs/midi'
import { Scissors, Trash2, Download, X } from 'lucide-react'

interface Clip {
  id: string
  sourceStart: number
  sourceEnd: number
}

const PIXELS_PER_SECOND = 60
const TOUR_STORAGE_KEY = 'apnasargam_seen_editor_tour'

const TOUR_STEPS = [
  {
    title: 'This is your track',
    body: 'Each purple block is a clip of your generated music, laid out left to right in time.',
  },
  {
    title: 'Choose where to cut',
    body: 'Drag this slider to move the playhead to the exact second you want to cut at.',
  },
  {
    title: 'Split the clip',
    body: 'Click "Split Here" to cut the clip in two at the playhead position.',
  },
  {
    title: 'Select, delete, apply',
    body: 'Click any clip to select it (it turns gold). Use the trash icon to remove it, then "Apply Edits" to save your changes -- the gap closes automatically.',
  },
]

export default function TimelineEditor({ midiUrl, onExport }: { midiUrl: string; onExport: (url: string) => void }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [originalMidi, setOriginalMidi] = useState<Midi | null>(null)
  const [clips, setClips] = useState<Clip[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [playheadTime, setPlayheadTime] = useState(0)

  const [tourStep, setTourStep] = useState<number | null>(null)

  useEffect(() => {
    const alreadySeen = localStorage.getItem(TOUR_STORAGE_KEY)
    if (!alreadySeen) {
      setTourStep(0)
    }
  }, [])

  const advanceTour = () => {
    if (tourStep === null) return
    if (tourStep >= TOUR_STEPS.length - 1) {
      localStorage.setItem(TOUR_STORAGE_KEY, 'true')
      setTourStep(null)
    } else {
      setTourStep(tourStep + 1)
    }
  }

  const skipTour = () => {
    localStorage.setItem(TOUR_STORAGE_KEY, 'true')
    setTourStep(null)
  }

  useEffect(() => {
    fetch(midiUrl)
      .then((res) => res.arrayBuffer())
      .then((buffer) => {
        const midi = new Midi(buffer)
        setOriginalMidi(midi)
        setClips([{ id: 'clip-0', sourceStart: 0, sourceEnd: midi.duration }])
      })
  }, [midiUrl])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.fillStyle = '#0A0A0F'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    let cursorX = 4
    clips.forEach((clip) => {
      const width = (clip.sourceEnd - clip.sourceStart) * PIXELS_PER_SECOND
      const isSelected = clip.id === selectedId

      ctx.fillStyle = isSelected ? '#E8A33D' : '#6C5CE7'
      ctx.fillRect(cursorX, 8, Math.max(width - 3, 2), canvas.height - 16)

      ctx.fillStyle = isSelected ? 'rgba(0,0,0,0.15)' : 'rgba(255,255,255,0.15)'
      for (let x = cursorX + 4; x < cursorX + width - 4; x += 5) {
        const barHeight = 6 + Math.random() * (canvas.height - 24)
        ctx.fillRect(x, (canvas.height - barHeight) / 2, 2, barHeight)
      }

      cursorX += width
    })
  }, [clips, selectedId])

  const hitTest = (clickX: number): Clip | null => {
    let cursorX = 4
    for (const clip of clips) {
      const width = (clip.sourceEnd - clip.sourceStart) * PIXELS_PER_SECOND
      if (clickX >= cursorX && clickX <= cursorX + width) return clip
      cursorX += width
    }
    return null
  }

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current!.getBoundingClientRect()
    const clickX = e.clientX - rect.left
    const hit = hitTest(clickX)
    if (hit) setSelectedId(hit.id)
  }

  const handleSplitAtPlayhead = () => {
    const hit = clips.find((c) => playheadTime >= c.sourceStart && playheadTime <= c.sourceEnd)
    if (!hit) return
    if (playheadTime <= hit.sourceStart || playheadTime >= hit.sourceEnd) return

    setClips((prev) => {
      const index = prev.findIndex((c) => c.id === hit.id)
      const before: Clip = { id: `${hit.id}-a-${Date.now()}`, sourceStart: hit.sourceStart, sourceEnd: playheadTime }
      const after: Clip = { id: `${hit.id}-b-${Date.now()}`, sourceStart: playheadTime, sourceEnd: hit.sourceEnd }
      const next = [...prev]
      next.splice(index, 1, before, after)
      return next
    })
  }

  const handleDelete = () => {
    if (!selectedId || clips.length <= 1) return
    setClips((prev) => prev.filter((c) => c.id !== selectedId))
    setSelectedId(null)
  }

  const handleApply = () => {
    if (!originalMidi) return

    const newMidi = new Midi()
    newMidi.header.setTempo(originalMidi.header.tempos[0]?.bpm || 120)

    originalMidi.tracks.forEach((sourceTrack) => {
      const newTrack = newMidi.addTrack()
      newTrack.instrument.number = sourceTrack.instrument.number
      if (sourceTrack.channel === 9) newTrack.channel = 9

      let outputCursor = 0
      clips.forEach((clip) => {
        const clipDuration = clip.sourceEnd - clip.sourceStart
        sourceTrack.notes.forEach((note) => {
          if (note.time >= clip.sourceStart && note.time < clip.sourceEnd) {
            newTrack.addNote({
              midi: note.midi,
              time: outputCursor + (note.time - clip.sourceStart),
              duration: Math.min(note.duration, clip.sourceEnd - note.time),
              velocity: note.velocity,
            })
          }
        })
        outputCursor += clipDuration
      })
    })

    const bytes = newMidi.toArray()
    const blob = new Blob([bytes as BlobPart], { type: 'audio/midi' })
    const url = URL.createObjectURL(blob)
    onExport(url)
  }

  return (
    <div className="relative rounded-2xl border border-white/10 bg-bg-soft p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <h3 className="font-semibold text-sm">Edit Track</h3>
          <button
            onClick={() => setTourStep(0)}
            className="text-[11px] text-muted hover:text-gold underline"
          >
            How does this work?
          </button>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleDelete}
            disabled={!selectedId || clips.length <= 1}
            className="p-2 rounded-lg text-red-400 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/5"
            title="Delete selected clip"
          >
            <Trash2 size={16} />
          </button>
          <button
            onClick={handleApply}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gold text-black text-xs font-semibold"
          >
            <Download size={14} />
            Apply Edits
          </button>
        </div>
      </div>

      <div className="flex items-center gap-4 mb-2 text-[11px] text-muted">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-indigo inline-block" /> Clip
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-gold inline-block" /> Selected
        </span>
      </div>

      <canvas
        ref={canvasRef}
        width={800}
        height={70}
        onClick={handleCanvasClick}
        className="w-full rounded-lg cursor-pointer"
      />

      <div className="mt-3 flex items-center gap-3">
        <span className="text-[11px] text-muted whitespace-nowrap">Cut position</span>
        <input
          type="range"
          min={0}
          max={originalMidi?.duration || 10}
          step={0.1}
          value={playheadTime}
          onChange={(e) => setPlayheadTime(Number(e.target.value))}
          className="flex-1 accent-gold"
        />
        <span className="text-xs text-muted w-14">{playheadTime.toFixed(1)}s</span>
        <button
          onClick={handleSplitAtPlayhead}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/10 text-xs hover:border-white/25 whitespace-nowrap"
        >
          <Scissors size={13} /> Split Here
        </button>
      </div>

      {tourStep !== null && (
        <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/70 backdrop-blur-sm rounded-2xl p-6">
          <div className="w-full max-w-sm rounded-2xl border border-white/10 bg-bg-soft p-6 relative">
            <button onClick={skipTour} className="absolute top-3 right-3 text-muted hover:text-text">
              <X size={16} />
            </button>
            <div className="text-[11px] text-gold font-semibold mb-2">
              Step {tourStep + 1} of {TOUR_STEPS.length}
            </div>
            <h4 className="font-semibold text-base mb-2">{TOUR_STEPS[tourStep].title}</h4>
            <p className="text-sm text-muted leading-relaxed mb-5">{TOUR_STEPS[tourStep].body}</p>
            <div className="flex items-center justify-between">
              <button onClick={skipTour} className="text-xs text-muted hover:text-text">
                Skip
              </button>
              <button
                onClick={advanceTour}
                className="px-4 py-2 rounded-full bg-gold text-black text-xs font-semibold"
              >
                {tourStep >= TOUR_STEPS.length - 1 ? 'Got it' : 'Next'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
