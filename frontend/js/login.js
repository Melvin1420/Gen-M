(function () {
  if (isLoggedIn()) {
    window.location.href = "/dashboard.html";
    return;
  }

  const form = document.getElementById("login-form");
  const errorEl = document.getElementById("error-message");
  const submitBtn = document.getElementById("submit-btn");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorEl.hidden = true;

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
      errorEl.textContent = "Enter your email and password.";
      errorEl.hidden = false;
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Signing in...";

    try {
      await login(email, password);
      window.location.href = "/dashboard.html";
    } catch (err) {
      errorEl.textContent = err.message || "Sign in failed.";
      errorEl.hidden = false;
      submitBtn.disabled = false;
      submitBtn.textContent = "Sign in";
    }
  });
})();
