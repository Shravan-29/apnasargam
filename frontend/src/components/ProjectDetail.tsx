import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Pencil, Trash2, Check, X } from 'lucide-react'
import {
  fetchProjects,
  getProjectMidiUrl,
  updateProject,
  deleteProject,
  saveEditedMidi,
} from '../api'
import ReactiveVisualizer from './ReactiveVisualizer'
import TimelineEditor from './TimelineEditor'

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

  const [isRenaming, setIsRenaming] = useState(false)
  const [nameInput, setNameInput] = useState('')
  const [renaming, setRenaming] = useState(false)

  const [deleting, setDeleting] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)

  const [previewMidiUrl, setPreviewMidiUrl] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)
  const editedBlobRef = useRef<Blob | null>(null)

  const playerRef = useRef<HTMLElement>(null)
  const previewPlayerRef = useRef<HTMLElement>(null)

  const token = localStorage.getItem('apnasargam_token') || ''

  const loadProject = () => {
    fetchProjects(token)
      .then((data: Project[]) => {
        const found = data.find((p) => String(p.id) === id)
        setProject(found || null)
        if (found) setNameInput(found.name)
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }
    loadProject()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  const handleRename = async () => {
    if (!project || !nameInput.trim()) return
    setRenaming(true)
    try {
      const updated = await updateProject(token, project.id, { name: nameInput.trim() })
      setProject({ ...project, name: updated.name })
      setIsRenaming(false)
    } finally {
      setRenaming(false)
    }
  }

  const handleDelete = async () => {
    if (!project) return
    setDeleting(true)
    try {
      await deleteProject(token, project.id)
      navigate('/dashboard')
    } finally {
      setDeleting(false)
    }
  }

  const handlePreviewExport = (url: string, blob: Blob) => {
    setPreviewMidiUrl(url)
    editedBlobRef.current = blob
    setSaveMessage(null)
  }

  const handleSaveEdit = async () => {
    if (!project || !editedBlobRef.current) return
    setSaving(true)
    setSaveMessage(null)
    try {
      const updated = await saveEditedMidi(token, project.id, editedBlobRef.current)
      setProject({ ...project, midi_filename: updated.midi_filename })
      setPreviewMidiUrl(null)
      editedBlobRef.current = null
      setSaveMessage('Saved. This is now the project track.')
    } catch {
      setSaveMessage('Could not save the edit. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleDiscardPreview = () => {
    setPreviewMidiUrl(null)
    editedBlobRef.current = null
    setSaveMessage(null)
  }

  if (loading) {
    return <div className="px-6 md:px-12 py-16">Loading...</div>
  }

  if (!project) {
    return (
      <div className="px-6 md:px-12 py-16">
        <p className="text-muted">Project not found.</p>
        <Link to="/dashboard" className="text-gold hover:underline text-sm">Back to Dashboard</Link>
      </div>
    )
  }

  const midiUrl = project.midi_filename ? getProjectMidiUrl(project.midi_filename, token) : null

  return (
    <div className="px-6 md:px-12 py-10 md:py-16 max-w-3xl mx-auto">
      <Link to="/dashboard" className="text-sm text-muted hover:text-text">&larr; Back to Dashboard</Link>

      <div className="mt-4 mb-8 flex items-center justify-between gap-4">
        {isRenaming ? (
          <div className="flex items-center gap-2 flex-1">
            <input
              value={nameInput}
              onChange={(e) => setNameInput(e.target.value)}
              autoFocus
              className="font-display text-xl font-bold bg-bg-soft border border-white/10 rounded-lg px-3 py-1.5 flex-1 outline-none focus:border-gold"
            />
            <button
              onClick={handleRename}
              disabled={renaming}
              className="p-2 rounded-lg bg-gold text-black disabled:opacity-50"
            >
              <Check size={16} />
            </button>
            <button
              onClick={() => { setIsRenaming(false); setNameInput(project.name) }}
              className="p-2 rounded-lg border border-white/10 text-muted hover:text-text"
            >
              <X size={16} />
            </button>
          </div>
        ) : (
          <>
            <h1 className="font-display text-3xl font-bold">{project.name}</h1>
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => setIsRenaming(true)}
                className="p-2 rounded-lg text-muted hover:text-text hover:bg-white/5"
                title="Rename"
              >
                <Pencil size={16} />
              </button>
              <button
                onClick={() => setConfirmingDelete(true)}
                className="p-2 rounded-lg text-red-400 hover:bg-white/5"
                title="Delete project"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </>
        )}
      </div>

      {confirmingDelete && (
        <div className="mb-6 rounded-2xl border border-red-400/30 bg-red-400/5 p-5 flex items-center justify-between gap-4">
          <p className="text-sm">Delete "{project.name}" permanently? This can't be undone.</p>
          <div className="flex gap-2 shrink-0">
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="px-4 py-2 rounded-full bg-red-400 text-black text-sm font-semibold disabled:opacity-50"
            >
              {deleting ? 'Deleting...' : 'Delete'}
            </button>
            <button
              onClick={() => setConfirmingDelete(false)}
              className="px-4 py-2 rounded-full border border-white/10 text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-white/10 bg-bg-soft p-6 md:p-8">
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

            <div className="mt-6">
              <TimelineEditor midiUrl={midiUrl} onExport={handlePreviewExport} />
            </div>

            {previewMidiUrl && (
              <div className="mt-6 rounded-2xl border border-gold/30 bg-gold/5 p-5">
                <p className="text-sm font-medium mb-3">Preview of your edit</p>
                {/* @ts-expect-error - web component */}
                <midi-player ref={previewPlayerRef} src={previewMidiUrl} sound-font style={{ width: '100%' }} />

                <div className="flex items-center gap-3 mt-4">
                  <button
                    onClick={handleSaveEdit}
                    disabled={saving}
                    className="px-5 py-2.5 rounded-full bg-gold text-black text-sm font-semibold disabled:opacity-50"
                  >
                    {saving ? 'Saving...' : 'Save to Project'}
                  </button>
                  <button
                    onClick={handleDiscardPreview}
                    className="px-5 py-2.5 rounded-full border border-white/10 text-sm"
                  >
                    Discard
                  </button>
                </div>
                {saveMessage && <p className="text-xs text-muted mt-3">{saveMessage}</p>}
              </div>
            )}
          </>
        ) : (
          <p className="text-muted text-sm">No generated audio for this project yet.</p>
        )}
      </div>
    </div>
  )
}
