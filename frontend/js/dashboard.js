(function () {
  if (!requireLogin()) {
    return;
  }
  initShell();

  const errorEl = document.getElementById("load-error");
  const emptyEl = document.getElementById("empty-state");
  const list = document.getElementById("attention-list");
  const totalCountEl = document.getElementById("stat-total");
  const urgentCountEl = document.getElementById("stat-urgent");

  const ACTIVE_STATUSES = ["open", "in_progress"];
  const PRIORITY_RANK = { urgent: 0, high: 1, medium: 2, low: 3 };

  function renderList(tickets) {
    if (tickets.length === 0) {
      emptyEl.hidden = false;
      list.hidden = true;
      return;
    }

    list.replaceChildren();
    for (const ticket of tickets) {
      const row = document.createElement("li");
      row.className = "attention-row";

      const link = document.createElement("a");
      link.className = "row-link";
      link.href = `/ticket.html?id=${encodeURIComponent(ticket.id)}`;
      link.textContent = ticket.title;

      const badges = document.createElement("span");
      badges.className = "attention-badges";
      badges.append(makeBadge(ticket.priority), makeBadge(ticket.status));

      const date = document.createElement("span");
      date.className = "attention-date";
      date.textContent = formatDate(ticket.created_at);

      row.append(link, badges, date);
      list.appendChild(row);
    }

    list.hidden = false;
    emptyEl.hidden = true;
  }

  async function loadDashboard() {
    try {
      const response = await authFetch("/tickets");
      if (!response.ok) {
        throw new Error("Could not load tickets.");
      }
      const tickets = await response.json();
      const active = tickets.filter((t) => ACTIVE_STATUSES.includes(t.status));
      active.sort((a, b) => {
        const rankDiff = PRIORITY_RANK[a.priority] - PRIORITY_RANK[b.priority];
        if (rankDiff !== 0) return rankDiff;
        return parseApiDate(a.created_at) - parseApiDate(b.created_at);
      });

      totalCountEl.textContent = String(active.length);
      urgentCountEl.textContent = String(active.filter((t) => t.priority === "urgent").length);
      renderList(active);
    } catch (err) {
      errorEl.textContent = err.message || "Could not load tickets.";
      errorEl.hidden = false;
    }
  }

  loadShellUser();
  loadDashboard();
})();
