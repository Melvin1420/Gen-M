const API_BASE = "/api/v1";
const TOKEN_KEY = "gen_m_token";

function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  sessionStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY);
}

function isLoggedIn() {
  return Boolean(getToken());
}

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 401) {
    clearToken();
  }

  return response;
}

async function login(email, password) {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!response.ok) {
    let detail = "Incorrect email or password.";
    try {
      const data = await response.json();
      if (data.detail) detail = data.detail;
    } catch (err) {
      // response wasn't JSON, keep default message
    }
    throw new Error(detail);
  }

  const data = await response.json();
  setToken(data.access_token);
  return data;
}

async function getCurrentUser() {
  const response = await apiFetch("/auth/me");
  if (!response.ok) {
    throw new Error("Could not load current user.");
  }
  return response.json();
}
