(function () {
  if (!requireLogin()) {
    return;
  }
  initShell();

  const form = document.getElementById("new-ticket-form");
  const departmentSelect = document.getElementById("department");
  const loadError = document.getElementById("load-error");
  const submitError = document.getElementById("submit-error");
  const submitBtn = document.getElementById("submit-btn");

  async function loadDepartments() {
    try {
      const response = await authFetch("/departments");
      if (!response.ok) {
        throw new Error("Could not load departments.");
      }
      const departments = await response.json();

      departmentSelect.replaceChildren();
      if (departments.length === 0) {
        const opt = document.createElement("option");
        opt.textContent = "No departments available";
        opt.disabled = true;
        opt.selected = true;
        departmentSelect.appendChild(opt);
        submitBtn.disabled = true;
        return;
      }
      for (const dept of departments) {
        const opt = document.createElement("option");
        opt.value = String(dept.id);
        opt.textContent = dept.name;
        departmentSelect.appendChild(opt);
      }
    } catch (err) {
      loadError.textContent = err.message || "Could not load departments.";
      loadError.hidden = false;
      submitBtn.disabled = true;
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    submitError.hidden = true;

    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();
    const category = document.getElementById("category").value.trim();
    const departmentId = departmentSelect.value;
    const priority = document.getElementById("priority").value;

    if (!title || !description || !category || !departmentId) {
      submitError.textContent = "Fill in every field before submitting.";
      submitError.hidden = false;
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Creating...";

    try {
      const response = await authFetch("/tickets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          description,
          category,
          department_id: Number(departmentId),
          priority,
        }),
      });
      if (!response.ok) {
        throw new Error(await readError(response, "Could not create the ticket."));
      }
      const ticket = await response.json();
      window.location.href = `/ticket.html?id=${encodeURIComponent(ticket.id)}`;
    } catch (err) {
      submitError.textContent = err.message || "Could not create the ticket.";
      submitError.hidden = false;
      submitBtn.disabled = false;
      submitBtn.textContent = "Create ticket";
    }
  });

  loadDepartments();
  loadShellUser();
})();
