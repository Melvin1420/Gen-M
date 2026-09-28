// Shared helpers for every authenticated page (everything except the login page).

function requireLogin() {
  if (!isLoggedIn()) {
    window.location.href = "/index.html";
    return false;
  }
  return true;
}

function initShell() {
  const signOutBtn = document.getElementById("sign-out-btn");
  signOutBtn.addEventListener("click", () => {
    clearToken();
    window.location.href = "/index.html";
  });
}

async function loadShellUser() {
  try {
    const user = await getCurrentUser();
    document.getElementById("current-user").textContent = `${user.email} \u00b7 ${user.role}`;
    return user;
  } catch (err) {
    window.location.href = "/index.html";
    return null;
  }
}

// Like apiFetch, but an expired/invalid session sends the user back to login.
async function authFetch(path, options) {
  const response = await apiFetch(path, options);
  if (response.status === 401) {
    window.location.href = "/index.html";
  }
  return response;
}

async function readError(response, fallback) {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") {
      return data.detail;
    }
  } catch (err) {
    // body wasn't JSON; fall through to the fallback message
  }
  return fallback;
}

function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatDateTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function makeBadge(value) {
  const badge = document.createElement("span");
  badge.className = `badge badge-${value}`;
  badge.textContent = value.replace("_", " ");
  return badge;
}
