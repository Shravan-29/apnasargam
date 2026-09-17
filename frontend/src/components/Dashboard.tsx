import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchProjects, createProject } from '../api'
import { Link } from 'react-router-dom'

interface Project {
  id: number
  name: string
  genre: string | null
  mood: string | null
  bpm: number | null
  musical_key: string | null
}

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [creating, setCreating] = useState(false)

  const [name, setName] = useState('')
  const [genre, setGenre] = useState('')
  const [mood, setMood] = useState('')
  const [bpm, setBpm] = useState(120)
  const [musicalKey, setMusicalKey] = useState('')

  const navigate = useNavigate()

  const loadProjects = () => {
    const token = localStorage.getItem('apnasargam_token')
    if (!token) {
      navigate('/login')
      return
    }

    setLoading(true)
    fetchProjects(token)
      .then((data) => setProjects(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadProjects()
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    const token = localStorage.getItem('apnasargam_token')
    if (!token) return

    setCreating(true)
    try {
      await createProject(token, { name, genre, mood, bpm, musical_key: musicalKey })
      setName('')
      setGenre('')
      setMood('')
      setBpm(120)
      setMusicalKey('')
      setShowForm(false)
      loadProjects()
    } catch (err) {
      setError('Failed to create project')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg text-text px-12 py-16">
      <div className="flex items-center justify-between mb-12">
  <h1 className="font-display text-3xl font-bold">My Projects</h1>
  <div className="flex gap-3">
    <Link
      to="/generate"
      className="px-5 py-2.5 rounded-full bg-gold text-black text-sm font-semibold hover:-translate-y-0.5 transition-transform"
    >
      Generate Music
    </Link>
    <button
      onClick={() => setShowForm(!showForm)}
      className="px-5 py-2.5 rounded-full bg-gold text-black text-sm font-semibold hover:-translate-y-0.5 transition-transform"
    >
      {showForm ? 'Cancel' : '+ New Project'}
    </button>
  </div>
</div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="mb-12 rounded-2xl border border-white/10 bg-bg-soft p-8 grid grid-cols-1 md:grid-cols-2 gap-5"
        >
          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-muted">Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="rounded-lg border border-white/10 bg-bg px-4 py-2.5 text-sm outline-none focus:border-gold transition-colors"
            />
          </div>
          <div className="flex flex-col gap-1.5">
  <label className="text-sm text-muted">Genre</label>
  <select
    value={genre}
    onChange={(e) => setGenre(e.target.value)}
    required
    className="rounded-lg border border-white/10 bg-bg px-4 py-2.5 text-sm outline-none focus:border-gold transition-colors"
  >
    <option value="">Select genre</option>
    <option value="Cinematic">Cinematic</option>
    <option value="Lo-fi">Lo-fi</option>
    <option value="Ambient">Ambient</option>
    <option value="Electronic">Electronic</option>
    <option value="Classical">Classical</option>
    <option value="Jazz">Jazz</option>
    <option value="Rock">Rock</option>
    <option value="Hip-hop">Hip-hop</option>
  </select>
</div>
          <div className="flex flex-col gap-1.5">
  <label className="text-sm text-muted">Mood</label>
  <select
    value={mood}
    onChange={(e) => setMood(e.target.value)}
    required
    className="rounded-lg border border-white/10 bg-bg px-4 py-2.5 text-sm outline-none focus:border-gold transition-colors"
  >
    <option value="">Select mood</option>
    <option value="Dark">Dark</option>
    <option value="Uplifting">Uplifting</option>
    <option value="Calm">Calm</option>
    <option value="Energetic">Energetic</option>
    <option value="Melancholic">Melancholic</option>
    <option value="Epic">Epic</option>
    <option value="Romantic">Romantic</option>
  </select>
</div>
          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-muted">BPM</label>
            <input
              type="number"
              value={bpm}
              onChange={(e) => setBpm(Number(e.target.value))}
              className="rounded-lg border border-white/10 bg-bg px-4 py-2.5 text-sm outline-none focus:border-gold transition-colors"
            />
          </div>
          <div className="flex flex-col gap-1.5 md:col-span-2">
            <label className="text-sm text-muted">Musical Key</label>
            <input
              value={musicalKey}
              onChange={(e) => setMusicalKey(e.target.value)}
              placeholder="e.g. A Minor"
              className="rounded-lg border border-white/10 bg-bg px-4 py-2.5 text-sm outline-none focus:border-gold transition-colors"
            />
          </div>
          <button
            type="submit"
            disabled={creating}
            className="md:col-span-2 mt-2 rounded-full bg-gold text-black font-semibold py-3 text-sm hover:-translate-y-0.5 transition-transform disabled:opacity-50"
          >
            {creating ? 'Creating...' : 'Create Project'}
          </button>
        </form>
      )}

      {loading && <p className="text-muted">Loading projects...</p>}
      {error && <p className="text-red-400">{error}</p>}

      {!loading && !error && projects.length === 0 && (
        <p className="text-muted">No projects yet. Create your first one!</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {projects.map((project) => (
          <div
            key={project.id}
            className="rounded-2xl border border-white/10 bg-bg-soft p-6 hover:border-white/20 transition-colors"
          >
            <h3 className="font-semibold text-lg mb-2">{project.name}</h3>
            <p className="text-muted text-sm">
              {project.genre} · {project.mood} · {project.bpm} BPM
            </p>
            {project.musical_key && (
              <p className="text-gold text-xs mt-2 font-medium">
                {project.musical_key}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}