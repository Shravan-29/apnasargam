import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { fetchProjects, getProjectMidiUrl } from '../api'
import ReactiveVisualizer from './ReactiveVisualizer'

interface Project {
  id: number
  name: string
  genre: string | null
  mood: string | null
  bpm: number | null
  musical_key: string | null
  midi_filename: string | null
  created_at: string
}

export default function ProjectDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const playerRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const token = localStorage.getItem('apnasargam_token')
    if (!token) {
      navigate('/login')
      return
    }

    fetchProjects(token)
      .then((data: Project[]) => {
        const found = data.find((p) => String(p.id) === id)
        setProject(found || null)
      })
      .finally(() => setLoading(false))
  }, [id, navigate])

  const token = localStorage.getItem('apnasargam_token') || ''

  if (loading) {
    return <div className="min-h-screen bg-bg text-text px-12 py-16">Loading...</div>
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-bg text-text px-12 py-16">
        <p className="text-muted">Project not found.</p>
        <Link to="/dashboard" className="text-gold hover:underline text-sm">Back to Dashboard</Link>
      </div>
    )
  }

  const midiUrl = project.midi_filename ? getProjectMidiUrl(project.midi_filename, token) : null

  return (
    <div className="min-h-screen bg-bg text-text px-12 py-16">
      <Link to="/dashboard" className="text-sm text-muted hover:text-text">&larr; Back to Dashboard</Link>

      <h1 className="font-display text-3xl font-bold mt-4 mb-8">{project.name}</h1>

      <div className="max-w-xl rounded-2xl border border-white/10 bg-bg-soft p-8">
        <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
          <div>
            <span className="text-muted">Genre</span>
            <p className="font-medium">{project.genre || 'None'}</p>
          </div>
          <div>
            <span className="text-muted">Mood</span>
            <p className="font-medium">{project.mood || 'None'}</p>
          </div>
          <div>
            <span className="text-muted">BPM</span>
            <p className="font-medium">{project.bpm ?? 'N/A'}</p>
          </div>
          <div>
            <span className="text-muted">Key</span>
            <p className="font-medium">{project.musical_key || 'N/A'}</p>
          </div>
          <div className="col-span-2">
            <span className="text-muted">Created</span>
            <p className="font-medium">{new Date(project.created_at).toLocaleString()}</p>
          </div>
        </div>

        {midiUrl ? (
          <>
            {/* @ts-expect-error - html-midi-player is a web component without TS types */}
            <midi-player ref={playerRef} src={midiUrl} sound-font style={{ width: '100%' }} />
            <div className="mt-3">
              <ReactiveVisualizer playerRef={playerRef} />
            </div>
            <a href={midiUrl} download className="inline-block mt-4 text-sm text-gold hover:underline">
              Download MIDI
            </a>
          </>
        ) : (
          <p className="text-muted text-sm">No generated audio for this project yet.</p>
        )}
      </div>
    </div>
  )
}
