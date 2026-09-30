import { useState, useRef, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { generateMusic, generateFromPrompt, getJobStatus, getMidiDownloadUrl, fetchProjects } from '../api'
import TimelineEditor from './TimelineEditor'
import ReactiveVisualizer from './ReactiveVisualizer'

const KEYS = ['C Major', 'A Minor', 'D Minor', 'F# Minor', 'G Major']
const MOODS = ['Dark', 'Uplifting', 'Calm', 'Energetic', 'Melancholic', 'Epic', 'Romantic']
const GENRES = ['Cinematic', 'Lo-fi', 'Ambient', 'Electronic', 'Classical', 'Jazz', 'Rock', 'Hip-hop']

interface RecentProject {
  id: number
  name: string
  genre: string | null
  mood: string | null
  bpm: number | null
}

function RecentTracks({ refreshKey }: { refreshKey: number }) {
  const [projects, setProjects] = useState<RecentProject[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('apnasargam_token')
    if (!token) return
    fetchProjects(token)
      .then((data: RecentProject[]) => setProjects(data.slice(-6).reverse()))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [refreshKey])

  return (
    <div className="rounded-2xl border border-white/10 bg-bg-soft p-6">
      <h3 className="font-semibold text-sm mb-4">Recent Tracks</h3>

      {loading && <p className="text-xs text-muted">Loading...</p>}

      {!loading && projects.length === 0 && (
        <p className="text-xs text-muted">Your generated tracks will show up here.</p>
      )}

      <div className="flex flex-col gap-3">
        {projects.map((project) => (
          <Link
            key={project.id}
            to={`/project/${project.id}`}
            className="rounded-xl border border-white/10 p-3.5 hover:border-white/25 transition-colors"
          >
            <p className="text-sm font-medium truncate">{project.name}</p>
            <p className="text-xs text-muted mt-1">
              {[project.genre, project.mood, project.bpm ? `${project.bpm} BPM` : null]
                .filter(Boolean)
                .join(' · ')}
            </p>
          </Link>
        ))}
      </div>

      <Link to="/dashboard" className="block mt-4 text-xs text-gold hover:underline">
        View all projects
      </Link>
    </div>
  )
}

function Tips() {
  return (
    <div className="rounded-2xl border border-white/10 bg-bg-soft p-6">
      <h3 className="font-semibold text-sm mb-3">Tips</h3>
      <ul className="text-xs text-muted flex flex-col gap-2 leading-relaxed">
        <li>Calm and Uplifting moods generate sparser, gentler melodies.</li>
        <li>Energetic and Rock/Electronic genres add a drum track automatically.</li>
        <li>Indian folk style ignores Key and Genre and picks a raga from the mood instead.</li>
        <li>Every track is 1-2 minutes: intro, verse, chorus, verse, chorus, outro.</li>
      </ul>
    </div>
  )
}

export default function Generator() {
  const [mode, setMode] = useState<'structured' | 'prompt'>('prompt')

  const [projectName, setProjectName] = useState('')
  const [key, setKey] = useState('A Minor')
  const [mood, setMood] = useState('Dark')
  const [bpm, setBpm] = useState(110)
  const [prompt, setPrompt] = useState('')
  const [genre, setGenre] = useState('')
  const [indianFolk, setIndianFolk] = useState(false)

  const [status, setStatus] = useState<'idle' | 'queued' | 'generating' | 'ready' | 'error'>('idle')
  const [jobId, setJobId] = useState<string | null>(null)
  const [predictedMood, setPredictedMood] = useState<string | null>(null)
  const [currentMidiUrl, setCurrentMidiUrl] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const playerRef = useRef<HTMLElement>(null)
  const navigate = useNavigate()

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    const token = localStorage.getItem('apnasargam_token')
    if (!token) {
      navigate('/login')
      return
    }

    setStatus('queued')
    setPredictedMood(null)
    setCurrentMidiUrl(null)

    const style = indianFolk ? 'indian_folk' : 'western'
    const genreToSend = indianFolk ? undefined : genre || undefined

    try {
      const job =
        mode === 'prompt'
          ? await generateFromPrompt(token, { project_name: projectName, prompt, key, bpm, genre: genreToSend, style })
          : await generateMusic(token, { project_name: projectName, key, mood, bpm, genre: genreToSend, style })
      setJobId(job.job_id)
      pollJobStatus(token, job.job_id)
    } catch {
      setStatus('error')
    }
  }

  const pollJobStatus = (token: string, id: string) => {
    setStatus('generating')
    const interval = setInterval(async () => {
      try {
        const data = await getJobStatus(token, id)
        if (data.status === 'finished') {
          clearInterval(interval)
          setStatus('ready')
          if (data.result?.predicted_mood) {
            setPredictedMood(data.result.predicted_mood)
          }
          setCurrentMidiUrl(getMidiDownloadUrl(id, token))
          setRefreshKey((k) => k + 1)
        } else if (data.status === 'failed') {
          clearInterval(interval)
          setStatus('error')
        }
      } catch {
        clearInterval(interval)
        setStatus('error')
      }
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-bg text-text px-6 md:px-12 py-10 md:py-16">
      <h1 className="font-display text-3xl font-bold mb-6">Generate Music</h1>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-8 items-start">
        <div>
          <div className="flex gap-2 mb-8">
            <button
              onClick={() => setMode('prompt')}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
                mode === 'prompt' ? 'bg-gold text-black' : 'border border-white/10 text-muted'
              }`}
            >
              Describe it
            </button>
            <button
              onClick={() => setMode('structured')}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
                mode === 'structured' ? 'bg-gold text-black' : 'border border-white/10 text-muted'
              }`}
            >
              Pick parameters
            </button>
          </div>

          <form
            onSubmit={handleGenerate}
            className="rounded-2xl border border-white/10 bg-bg-soft p-6 md:p-8 flex flex-col gap-5"
          >
            <div className="flex flex-col gap-1.5">
              <label className="text-sm text-muted">Project Name</label>
              <input
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                required
                className="rounded-lg border border-white/10 bg-bg px-4 py-2.5 text-sm outline-none focus:border-gold transition-colors"
              />
            </div>

            {mode === 'prompt' ? (
              <div className="flex flex-col gap-1.5">
                <label className="text-sm text-muted">Describe the mood you want</label>
                <input
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  required
                  placeholder="e.g. sweet romantic love song"
                  className="rounded-lg border border-white/10 bg-bg px-4 py-2.5 text-sm outline-none focus:border-gold transition-colors"
                />
              </div>
            ) : (
              <div className="flex flex-col gap-1.5">
                <label className="text-sm text-muted">Mood</label>
                <select
                  value={mood}
                  onChange={(e) => setMood(e.target.value)}
                  className="rounded-lg border border-white/10 bg-bg px-4 py-2.5 text-sm outline-none focus:border-gold transition-colors"
                >
                  {MOODS.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
            )}

            <div className="grid grid-cols-2 gap-5">
              <div className="flex flex-col gap-1.5">
                <label className="text-sm text-muted">Key</label>
                <select
                  value={key}
                  onChange={(e) => setKey(e.target.value)}
                  disabled={indianFolk}
                  className="rounded-lg border border-white/10 bg-bg px-4 py-2.5 text-sm outline-none focus:border-gold transition-colors disabled:opacity-40"
                >
                  {KEYS.map((k) => (
                    <option key={k} value={k}>{k}</option>
                  ))}
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-sm text-muted">BPM: {bpm}</label>
                <input
                  type="range"
                  min={60}
                  max={180}
                  value={bpm}
                  onChange={(e) => setBpm(Number(e.target.value))}
                  className="accent-gold mt-2.5"
                />
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-sm text-muted">Genre (optional)</label>
              <select
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
                disabled={indianFolk}
                className="rounded-lg border border-white/10 bg-bg px-4 py-2.5 text-sm outline-none focus:border-gold transition-colors disabled:opacity-40"
              >
                <option value="">Default (mood-based instruments)</option>
                {GENRES.map((g) => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
            </div>

            <label className="flex items-center gap-3 rounded-lg border border-white/10 px-4 py-3 cursor-pointer">
              <input
                type="checkbox"
                checked={indianFolk}
                onChange={(e) => setIndianFolk(e.target.checked)}
                className="accent-gold w-4 h-4"
              />
              <div>
                <p className="text-sm font-medium">Indian folk style</p>
                <p className="text-xs text-muted">Uses a raga scale (Bhupali, Yaman or Bhairav) with flute, sitar and harmonium instead of key and genre.</p>
              </div>
            </label>

            <button
              type="submit"
              disabled={status === 'queued' || status === 'generating'}
              className="mt-2 rounded-full bg-gold text-black font-semibold py-3 text-sm hover:-translate-y-0.5 transition-transform disabled:opacity-50"
            >
              {status === 'idle' || status === 'ready' || status === 'error'
                ? 'Generate'
                : status === 'queued'
                ? 'Queued...'
                : 'Composing...'}
            </button>
          </form>

          {status === 'ready' && jobId && currentMidiUrl && (
            <div className="mt-8 rounded-2xl border border-white/10 bg-bg-soft p-6 md:p-8">
              <h3 className="font-semibold mb-2">Your track</h3>
              {predictedMood && <p className="text-sm text-gold mb-4">Detected mood: {predictedMood}</p>}

              {/* @ts-expect-error - html-midi-player is a web component without TS types */}
              <midi-player ref={playerRef} src={currentMidiUrl} sound-font style={{ width: '100%' }} />

              <div className="mt-3">
                <ReactiveVisualizer playerRef={playerRef} />
              </div>

              <a href={currentMidiUrl} download className="inline-block mt-4 text-sm text-gold hover:underline">
                Download MIDI
              </a>

              <div className="mt-6">
                <TimelineEditor midiUrl={currentMidiUrl} onExport={(url) => setCurrentMidiUrl(url)} />
              </div>
            </div>
          )}

          {status === 'error' && (
            <p className="mt-6 text-red-400">Something went wrong. Please try again.</p>
          )}
        </div>

        <div className="flex flex-col gap-6">
          <Tips />
          <RecentTracks refreshKey={refreshKey} />
        </div>
      </div>
    </div>
  )
}
