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

// The API returns naive UTC timestamps with no "Z"/offset marker (see GEN-16
// and GEN-19). Without one, JavaScript's Date parser treats a date-time
// string as LOCAL time, not UTC, which silently shows the wrong wall-clock
// hour to anyone not in the exact UTC+0 zone. Force UTC interpretation
// explicitly instead of trusting the string alone. If the API ever starts
// sending a real zone marker, this is a no-op - the check below skips it.
function parseApiDate(isoString) {
  const hasZone = /Z$|[+-]\d{2}:\d{2}$/.test(isoString);
  return new Date(hasZone ? isoString : `${isoString}Z`);
}

function formatDate(isoString) {
  const date = parseApiDate(isoString);
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatDateTime(isoString) {
  const date = parseApiDate(isoString);
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
