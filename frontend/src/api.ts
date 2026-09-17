const API_BASE_URL = 'http://localhost:8000'

export async function fetchProjects(token: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/projects/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Failed to fetch projects')
  }

  return response.json()
}
export async function loginUser(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  })

  if (!response.ok) {
    throw new Error('Invalid email or password')
  }

  return response.json()
}
export async function registerUser(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  })

  if (!response.ok) {
    const data = await response.json()
    throw new Error(data.detail || 'Registration failed')
  }

  return response.json()
}
export async function createProject(
  token: string,
  project: { name: string; genre: string; mood: string; bpm: number; musical_key: string }
) {
  const response = await fetch(`${API_BASE_URL}/api/v1/projects/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(project),
  })

  if (!response.ok) {
    throw new Error('Failed to create project')
  }

  return response.json()
}
export async function generateMusic(
  token: string,
  data: { project_name: string; key: string; mood: string; bpm: number }
) {
  const response = await fetch(`${API_BASE_URL}/api/v1/jobs/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to start generation')
  return response.json()
}

export async function getJobStatus(token: string, jobId: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/jobs/${jobId}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) throw new Error('Failed to fetch job status')
  return response.json()
}

export function getMidiDownloadUrl(jobId: string, token: string) {
  return `${API_BASE_URL}/api/v1/jobs/${jobId}/midi?token=${token}`
}