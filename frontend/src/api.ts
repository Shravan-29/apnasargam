const API_BASE_URL = 'http://localhost:8000'
const TOKEN_KEY = 'apnasargam_token'

// If the server says the token is invalid or expired, clear it and send the
// user to the login page instead of leaving them on a broken screen.
function handleSessionExpired(): never {
  localStorage.removeItem(TOKEN_KEY)
  window.location.href = '/login'
  throw new Error('Session expired')
}

async function authorizedFetch(
  url: string,
  token: string,
  options: { method?: string; body?: unknown } = {}
) {
  const headers: Record<string, string> = { Authorization: `Bearer ${token}` }
  if (options.body !== undefined) headers['Content-Type'] = 'application/json'

  const response = await fetch(url, {
    method: options.method || 'GET',
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  })

  if (response.status === 401) return handleSessionExpired()
  return response
}

export async function fetchProjects(token: string) {
  const response = await authorizedFetch(`${API_BASE_URL}/api/v1/projects/`, token)
  if (!response.ok) throw new Error('Failed to fetch projects')
  return response.json()
}

export async function createProject(
  token: string,
  project: { name: string; genre: string; mood: string; bpm: number; musical_key: string }
) {
  const response = await authorizedFetch(`${API_BASE_URL}/api/v1/projects/`, token, {
    method: 'POST',
    body: project,
  })
  if (!response.ok) throw new Error('Failed to create project')
  return response.json()
}

export async function loginUser(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!response.ok) throw new Error('Invalid email or password')
  return response.json()
}

export async function registerUser(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!response.ok) {
    const data = await response.json()
    throw new Error(data.detail || 'Registration failed')
  }
  return response.json()
}

export async function generateMusic(
  token: string,
  data: { project_name: string; key: string; mood: string; bpm: number; genre?: string; style?: string }
) {
  const response = await authorizedFetch(`${API_BASE_URL}/api/v1/jobs/generate`, token, {
    method: 'POST',
    body: data,
  })
  if (!response.ok) throw new Error('Failed to start generation')
  return response.json()
}

export async function generateFromPrompt(
  token: string,
  data: { project_name: string; prompt: string; key: string; bpm: number; genre?: string; style?: string }
) {
  const response = await authorizedFetch(`${API_BASE_URL}/api/v1/jobs/generate-from-prompt`, token, {
    method: 'POST',
    body: data,
  })
  if (!response.ok) throw new Error('Failed to start generation')
  return response.json()
}

export async function getJobStatus(token: string, jobId: string) {
  const response = await authorizedFetch(`${API_BASE_URL}/api/v1/jobs/${jobId}`, token)
  if (!response.ok) throw new Error('Failed to fetch job status')
  return response.json()
}

export function getMidiDownloadUrl(jobId: string, token: string) {
  return `${API_BASE_URL}/api/v1/jobs/${jobId}/midi?token=${token}`
}

export function getProjectMidiUrl(filename: string, token: string) {
  return `${API_BASE_URL}/api/v1/jobs/midi-by-filename/${filename}?token=${token}`
}
