(function () {
  if (!requireLogin()) {
    return;
  }
  initShell();

  const STAFF_ROLES = ["it_agent", "manager", "admin"];
  const ASSIGN_ROLES = ["it_agent", "admin"];

  const $ = (id) => document.getElementById(id);
  const els = {
    loadError: $("load-error"),
    view: $("ticket-view"),
    title: $("ticket-title"),
    badges: $("ticket-badges"),
    meta: $("ticket-meta"),
    description: $("ticket-description"),
    editForm: $("edit-form"),
    textFields: $("text-fields"),
    editTitle: $("edit-title"),
    editDescription: $("edit-description"),
    staffFields: $("staff-fields"),
    editStatus: $("edit-status"),
    editPriority: $("edit-priority"),
    assigneeText: $("assignee-text"),
    assignBtn: $("assign-btn"),
    saveMessage: $("save-message"),
    saveError: $("save-error"),
    saveBtn: $("save-btn"),
    messageList: $("message-list"),
    messagesEmpty: $("messages-empty"),
    messageForm: $("message-form"),
    messageInput: $("message-input"),
    messageError: $("message-error"),
    messageBtn: $("message-btn"),
  };

  const ticketId = Number(new URLSearchParams(window.location.search).get("id"));
  let currentUser = null;
  let ticket = null;
  let departmentName = null;
  let messages = [];

  function isStaff() {
    return STAFF_ROLES.includes(currentUser.role);
  }

  // Mirrors the API rule: staff can edit text any time; a requester only while the ticket is open.
  function canEditText() {
    return isStaff() || (ticket.requester_id === currentUser.id && ticket.status === "open");
  }

  function userLabel(id) {
    if (id === null || id === undefined) {
      return "Unassigned";
    }
    return id === currentUser.id ? "You" : `User #${id}`;
  }

  function senderLabel(id) {
    if (id === currentUser.id) {
      return "You";
    }
    if (id === ticket.requester_id) {
      return "Requester";
    }
    if (id === ticket.assigned_agent_id) {
      return "Agent";
    }
    return `User #${id}`;
  }

  function showLoadError(message) {
    els.loadError.textContent = message;
    els.loadError.hidden = false;
    els.view.hidden = true;
  }

  function clearSaveFeedback() {
    els.saveMessage.hidden = true;
    els.saveError.hidden = true;
  }

  function showSaveMessage(message) {
    els.saveError.hidden = true;
    els.saveMessage.textContent = message;
    els.saveMessage.hidden = false;
  }

  function showSaveError(message) {
    els.saveMessage.hidden = true;
    els.saveError.textContent = message;
    els.saveError.hidden = false;
  }

  function addMeta(label, value) {
    const wrap = document.createElement("div");
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    wrap.append(dt, dd);
    els.meta.appendChild(wrap);
  }

  function renderTicket() {
    els.title.textContent = ticket.title;
    els.badges.replaceChildren(makeBadge(ticket.status), makeBadge(ticket.priority));
    els.description.textContent = ticket.description;

    els.meta.replaceChildren();
    addMeta("Category", ticket.category);
    addMeta("Department", departmentName || `Department #${ticket.department_id}`);
    addMeta("Requester", userLabel(ticket.requester_id));
    addMeta("Assigned to", userLabel(ticket.assigned_agent_id));
    addMeta("Created", formatDateTime(ticket.created_at));
    addMeta("Last updated", formatDateTime(ticket.updated_at));
    if (ticket.resolved_at) {
      addMeta("Resolved", formatDateTime(ticket.resolved_at));
    }

    const staff = isStaff();
    const textEditable = canEditText();
    els.editForm.hidden = !(staff || textEditable);
    els.textFields.hidden = !textEditable;
    els.staffFields.hidden = !staff;

    els.editTitle.value = ticket.title;
    els.editDescription.value = ticket.description;
    els.editStatus.value = ticket.status;
    els.editPriority.value = ticket.priority;

    els.assigneeText.textContent = `Assigned to: ${userLabel(ticket.assigned_agent_id)}`;
    els.assignBtn.hidden = !ASSIGN_ROLES.includes(currentUser.role);
    els.assignBtn.textContent =
      ticket.assigned_agent_id === currentUser.id ? "Unassign" : "Assign to me";
  }

  function renderMessages() {
    els.messageList.replaceChildren();
    els.messagesEmpty.hidden = messages.length > 0;

    for (const message of messages) {
      const item = document.createElement("li");
      item.className = message.sender_id === currentUser.id ? "message mine" : "message";

      const meta = document.createElement("div");
      meta.className = "message-meta";
      meta.textContent = `${senderLabel(message.sender_id)} \u00b7 ${formatDateTime(message.created_at)}`;

      const body = document.createElement("div");
      body.className = "message-body";
      body.textContent = message.message;

      item.append(meta, body);
      els.messageList.appendChild(item);
    }
  }

  async function patchTicket(payload, successText) {
    els.saveBtn.disabled = true;
    els.assignBtn.disabled = true;
    try {
      const response = await authFetch(`/tickets/${ticketId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error(await readError(response, "Could not save changes."));
      }
      ticket = await response.json();
      renderTicket();
      showSaveMessage(successText);
    } catch (err) {
      showSaveError(err.message || "Could not save changes.");
    } finally {
      els.saveBtn.disabled = false;
      els.assignBtn.disabled = false;
    }
  }

  els.editForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearSaveFeedback();

    // Only send fields that actually changed, and only ones this role may edit.
    const payload = {};

    if (canEditText()) {
      const title = els.editTitle.value.trim();
      const description = els.editDescription.value.trim();
      if (!title || !description) {
        showSaveError("Title and description can't be empty.");
        return;
      }
      if (title !== ticket.title) {
        payload.title = title;
      }
      if (description !== ticket.description) {
        payload.description = description;
      }
    }

    if (isStaff()) {
      if (els.editStatus.value !== ticket.status) {
        payload.status = els.editStatus.value;
      }
      if (els.editPriority.value !== ticket.priority) {
        payload.priority = els.editPriority.value;
      }
    }

    if (Object.keys(payload).length === 0) {
      showSaveMessage("No changes to save.");
      return;
    }
    await patchTicket(payload, "Changes saved.");
  });

  els.assignBtn.addEventListener("click", () => {
    clearSaveFeedback();
    const unassign = ticket.assigned_agent_id === currentUser.id;
    patchTicket(
      { assigned_agent_id: unassign ? null : currentUser.id },
      unassign ? "Ticket unassigned." : "Ticket assigned to you."
    );
  });

  els.messageForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    els.messageError.hidden = true;

    const text = els.messageInput.value.trim();
    if (!text) {
      els.messageError.textContent = "Write a message first.";
      els.messageError.hidden = false;
      return;
    }

    els.messageBtn.disabled = true;
    try {
      const response = await authFetch(`/tickets/${ticketId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      if (!response.ok) {
        throw new Error(await readError(response, "Could not send message."));
      }
      messages.push(await response.json());
      els.messageInput.value = "";
      renderMessages();
    } catch (err) {
      els.messageError.textContent = err.message || "Could not send message.";
      els.messageError.hidden = false;
    } finally {
      els.messageBtn.disabled = false;
    }
  });

  async function init() {
    if (!Number.isInteger(ticketId) || ticketId <= 0) {
      showLoadError("No ticket specified.");
      return;
    }

    currentUser = await loadShellUser();
    if (!currentUser) {
      return;
    }

    try {
      const ticketResponse = await authFetch(`/tickets/${ticketId}`);
      if (ticketResponse.status === 404) {
        showLoadError("Ticket not found.");
        return;
      }
      if (ticketResponse.status === 403) {
        showLoadError("You don't have access to this ticket.");
        return;
      }
      if (!ticketResponse.ok) {
        throw new Error("Could not load the ticket.");
      }
      ticket = await ticketResponse.json();

      const [departmentResponse, messagesResponse] = await Promise.all([
        authFetch(`/departments/${ticket.department_id}`),
        authFetch(`/tickets/${ticketId}/messages`),
      ]);
      if (departmentResponse.ok) {
        departmentName = (await departmentResponse.json()).name;
      }
      if (!messagesResponse.ok) {
        throw new Error("Could not load messages.");
      }
      messages = await messagesResponse.json();

      els.view.hidden = false;
      renderTicket();
      renderMessages();
    } catch (err) {
      showLoadError(err.message || "Could not load the ticket.");
    }
  }

  init();
})();
