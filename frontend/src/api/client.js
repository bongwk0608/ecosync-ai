const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
const TOKEN_KEY = "ecosync_auth_token";

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export async function fetchJson(path, options = {}) {
  const token = getStoredToken();
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Token ${token}` } : {}),
      ...(options.headers || {})
    },
    ...options
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export function registerUser(payload) {
  return fetchJson("/auth/register/", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function loginUser(payload) {
  const response = await fetchJson("/auth/login/", {
    method: "POST",
    body: JSON.stringify(payload)
  });
  setStoredToken(response.token);
  return response;
}

export function getCurrentUser() {
  return fetchJson("/auth/me/");
}

export async function logoutUser() {
  try {
    await fetchJson("/auth/logout/", { method: "POST" });
  } finally {
    setStoredToken("");
  }
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

export function createStartup(payload) {
  return fetchJson("/startups/", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function createMentor(payload) {
  return fetchJson("/mentors/", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function refreshRecommendationAi(recommendationId) {
  return fetchJson(`/recommendations/${recommendationId}/refresh-ai/`, {
    method: "POST"
  });
}
