import { useEffect, useState } from 'react'
import { fetchProjects } from '../api'

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

  useEffect(() => {
    // TEMPORARY: hardcoded token until login UI is built
    const token = localStorage.getItem('apnasargam_token')

    if (!token) {
      setError('Not logged in — no token found.')
      setLoading(false)
      return
    }

    fetchProjects(token)
      .then((data) => setProjects(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="min-h-screen bg-bg text-text px-12 py-16">
      <h1 className="font-display text-3xl font-bold mb-10">My Projects</h1>

      {loading && <p className="text-muted">Loading projects...</p>}
      {error && <p className="text-red-400">{error}</p>}

      {!loading && !error && projects.length === 0 && (
        <p className="text-muted">No projects yet. Create your first one!</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {projects.map((project) => (
          <div
            key={project.id}
            className="rounded-2xl border border-white/10 bg-bg-soft p-6"
          >
            <h3 className="font-semibold text-lg mb-2">{project.name}</h3>
            <p className="text-muted text-sm">
              {project.genre} · {project.mood} · {project.bpm} BPM
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}