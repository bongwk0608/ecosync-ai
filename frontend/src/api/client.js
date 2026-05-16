const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export function getInitialData() {
  return Promise.all([
    fetchJson("/cohorts/"),
    fetchJson("/programs/"),
    fetchJson("/partners/"),
    fetchJson("/startups/"),
    fetchJson("/mentors/"),
    fetchJson("/relationships/"),
    fetchJson("/dashboard/"),
    fetchJson("/evaluation/")
  ]);
}

export function runMatch(startupId) {
  return fetchJson("/match-runs/", {
    method: "POST",
    body: JSON.stringify({ startup_id: startupId })
  });
}

export function createRelationship(payload) {
  return fetchJson("/relationships/", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
