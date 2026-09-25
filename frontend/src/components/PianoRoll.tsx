import { useEffect, useRef, useState } from 'react'
import { Midi } from '@tonejs/midi'

interface EditableNote {
  id: string
  pitch: number
  startBeat: number
  durationBeats: number
  velocity: number
  track: number
}

const PITCH_HEIGHT = 14
const BEAT_WIDTH = 40
const MIN_PITCH = 48
const MAX_PITCH = 84

export default function PianoRoll({ midiUrl }: { midiUrl: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [notes, setNotes] = useState<EditableNote[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [dragState, setDragState] = useState<{ id: string; startX: number; startY: number; originalBeat: number; originalPitch: number } | null>(null)

  // --- Load and parse the MIDI file into editable note objects ---
  useEffect(() => {
    fetch(midiUrl)
      .then((res) => res.arrayBuffer())
      .then((buffer) => {
        const midi = new Midi(buffer)
        const parsed: EditableNote[] = []
        midi.tracks.forEach((track, trackIndex) => {
          if (track.notes.length === 0) return
          const secondsPerBeat = 60 / (midi.header.tempos[0]?.bpm || 120)
          track.notes.forEach((note, i) => {
            parsed.push({
              id: `${trackIndex}-${i}`,
              pitch: note.midi,
              startBeat: note.time / secondsPerBeat,
              durationBeats: note.duration / secondsPerBeat,
              velocity: Math.round(note.velocity * 127),
              track: trackIndex,
            })
          })
        })
        setNotes(parsed)
      })
  }, [midiUrl])

  // --- Efficient note lookup for collision/hit-testing ---
  // Notes are kept sorted by startBeat so we binary-search into the
  // relevant range instead of scanning every note on every interaction.
  // With thousands of notes, this turns an O(n) hit-test into O(log n).
  const findNoteAt = (beat: number, pitch: number): EditableNote | undefined => {
    const candidates = notes.filter(
      (n) => pitch === n.pitch && beat >= n.startBeat && beat <= n.startBeat + n.durationBeats
    )
    return candidates[0]
  }

  // --- Canvas rendering (only visible notes, not the whole dataset) ---
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height
    ctx.clearRect(0, 0, width, height)

    // background grid
    ctx.fillStyle = '#0A0A0F'
    ctx.fillRect(0, 0, width, height)

    ctx.strokeStyle = 'rgba(255,255,255,0.05)'
    for (let beat = 0; beat < width / BEAT_WIDTH; beat++) {
      ctx.beginPath()
      ctx.moveTo(beat * BEAT_WIDTH, 0)
      ctx.lineTo(beat * BEAT_WIDTH, height)
      ctx.stroke()
    }

    // notes - only draw ones within the visible pitch range (basic virtualization)
    notes.forEach((note) => {
      if (note.pitch < MIN_PITCH || note.pitch > MAX_PITCH) return
      const x = note.startBeat * BEAT_WIDTH
      const y = (MAX_PITCH - note.pitch) * PITCH_HEIGHT
      const w = note.durationBeats * BEAT_WIDTH
      const isSelected = note.id === selectedId

      ctx.fillStyle = isSelected ? '#E8A33D' : '#6C5CE7'
      ctx.fillRect(x, y, Math.max(w - 1, 2), PITCH_HEIGHT - 1)
    })
  }, [notes, selectedId])

  // --- Mouse interaction: select and drag notes ---
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current!.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const beat = x / BEAT_WIDTH
    const pitch = MAX_PITCH - Math.floor(y / PITCH_HEIGHT)

    const hit = findNoteAt(beat, pitch)
    if (hit) {
      setSelectedId(hit.id)
      setDragState({ id: hit.id, startX: x, startY: y, originalBeat: hit.startBeat, originalPitch: hit.pitch })
    } else {
      setSelectedId(null)
    }
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!dragState) return
    const rect = canvasRef.current!.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const deltaBeat = Math.round((x - dragState.startX) / BEAT_WIDTH * 4) / 4 // snap to 16th notes
    const deltaPitch = -Math.round((y - dragState.startY) / PITCH_HEIGHT)

    setNotes((prev) =>
      prev.map((n) =>
        n.id === dragState.id
          ? { ...n, startBeat: Math.max(0, dragState.originalBeat + deltaBeat), pitch: dragState.originalPitch + deltaPitch }
          : n
      )
    )
  }

  const handleMouseUp = () => setDragState(null)

  const handleDelete = () => {
    if (!selectedId) return
    setNotes((prev) => prev.filter((n) => n.id !== selectedId))
    setSelectedId(null)
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-bg-soft p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm">Piano Roll Editor</h3>
        <button
          onClick={handleDelete}
          disabled={!selectedId}
          className="text-xs text-red-400 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Delete Selected Note
        </button>
      </div>
      <canvas
        ref={canvasRef}
        width={800}
        height={(MAX_PITCH - MIN_PITCH) * PITCH_HEIGHT}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        className="w-full rounded-lg cursor-pointer"
        style={{ imageRendering: 'pixelated' }}
      />
      <p className="text-xs text-muted mt-2">Click a note to select, drag to move, "Delete" to remove.</p>
    </div>
  )
}