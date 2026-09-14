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