(function () {
  if (!requireLogin()) {
    return;
  }
  initShell();

  const errorEl = document.getElementById("load-error");
  const emptyEl = document.getElementById("empty-state");
  const table = document.getElementById("ticket-table");
  const tbody = document.getElementById("ticket-table-body");

  function renderTickets(tickets) {
    if (tickets.length === 0) {
      emptyEl.hidden = false;
      table.hidden = true;
      return;
    }

    tbody.replaceChildren();
    for (const ticket of tickets) {
      const row = document.createElement("tr");

      const titleCell = document.createElement("td");
      const link = document.createElement("a");
      link.className = "row-link";
      link.href = `/ticket.html?id=${encodeURIComponent(ticket.id)}`;
      link.textContent = ticket.title;
      titleCell.appendChild(link);

      const categoryCell = document.createElement("td");
      categoryCell.textContent = ticket.category;

      const priorityCell = document.createElement("td");
      priorityCell.appendChild(makeBadge(ticket.priority));

      const statusCell = document.createElement("td");
      statusCell.appendChild(makeBadge(ticket.status));

      const createdCell = document.createElement("td");
      createdCell.textContent = formatDate(ticket.created_at);

      row.append(titleCell, categoryCell, priorityCell, statusCell, createdCell);
      tbody.appendChild(row);
    }

    table.hidden = false;
    emptyEl.hidden = true;
  }

  async function loadTickets() {
    try {
      const response = await authFetch("/tickets");
      if (!response.ok) {
        throw new Error("Could not load tickets.");
      }
      renderTickets(await response.json());
    } catch (err) {
      errorEl.textContent = err.message || "Could not load tickets.";
      errorEl.hidden = false;
    }
  }

  loadShellUser();
  loadTickets();
})();
