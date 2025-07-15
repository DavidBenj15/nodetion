const API_BASE = import.meta.env.VITE_API_BASE || '';

export async function searchDocuments(query: string, topK: number = 3) {
  if (!API_BASE) {
    throw new Error('API_BASE is not set');
  }
  const response = await fetch(`${API_BASE}/documents?query=${query}&top_k=${topK}`);
  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }
  const res = await response.json();
  return res.results;
}
