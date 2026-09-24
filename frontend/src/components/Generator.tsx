import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { generateMusic, generateFromPrompt, getJobStatus, getMidiDownloadUrl } from '../api'

const KEYS = ['C Major', 'A Minor', 'D Minor', 'F# Minor', 'G Major']
const MOODS = ['Dark', 'Uplifting', 'Calm', 'Energetic', 'Melancholic', 'Epic', 'Romantic']

export default function Generator() {
  const [mode, setMode] = useState<'structured' | 'prompt'>('prompt')

  const [projectName, setProjectName] = useState('')
  const [key, setKey] = useState('A Minor')
  const [mood, setMood] = useState('Dark')
  const [bpm, setBpm] = useState(110)
  const [prompt, setPrompt] = useState('')

  const [status, setStatus] = useState<'idle' | 'queued' | 'generating' | 'ready' | 'error'>('idle')
  const [jobId, setJobId] = useState<string | null>(null)
  const [predictedMood, setPredictedMood] = useState<string | null>(null)
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
    try {
      const job =
        mode === 'prompt'
          ? await generateFromPrompt(token, { project_name: projectName, prompt, key, bpm })
          : await generateMusic(token, { project_name: projectName, key, mood, bpm })
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

  const token = localStorage.getItem('apnasargam_token') || ''

  return (
    <div className="min-h-screen bg-bg text-text px-12 py-16">
      <h1 className="font-display text-3xl font-bold mb-6">Generate Music</h1>

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
        className="max-w-xl rounded-2xl border border-white/10 bg-bg-soft p-8 flex flex-col gap-5"
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
              className="rounded-lg border border-white/10 bg-bg px-4 py-2.5 text-sm outline-none focus:border-gold transition-colors"
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

      {status === 'ready' && jobId && (
        <div className="max-w-xl mt-8 rounded-2xl border border-white/10 bg-bg-soft p-8">
          <h3 className="font-semibold mb-2">Your track is ready</h3>
          {predictedMood && (
            <p className="text-sm text-gold mb-4">Detected mood: {predictedMood}</p>
          )}
          {/* @ts-expect-error - web component */}
          <midi-player
            src={getMidiDownloadUrl(jobId, token)}
            sound-font
            visualizer="#myVisualizer"
          />
          {/* @ts-expect-error - web component */}
          <midi-visualizer id="myVisualizer" src={getMidiDownloadUrl(jobId, token)} />
          
           <a href={getMidiDownloadUrl(jobId, token)}
            download
            className="inline-block mt-4 text-sm text-gold hover:underline"
          >
            Download MIDI
          </a>
        </div>
      )}

      {status === 'error' && (
        <p className="mt-6 text-red-400">Something went wrong. Please try again.</p>
      )}
    </div>
  )
}