(function () {
  const form = document.getElementById("login-form");
  const errorEl = document.getElementById("error-message");
  const submitBtn = document.getElementById("submit-btn");
  const successEl = document.getElementById("success-message");
  const signedInAsEl = document.getElementById("signed-in-as");
  const signOutBtn = document.getElementById("sign-out-btn");

  async function showSignedInState() {
    try {
      const user = await getCurrentUser();
      form.hidden = true;
      successEl.hidden = false;
      signedInAsEl.textContent = `Signed in as ${user.email} (${user.role}).`;
    } catch (err) {
      clearToken();
    }
  }

  if (isLoggedIn()) {
    showSignedInState();
  }

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
      await showSignedInState();
    } catch (err) {
      errorEl.textContent = err.message || "Sign in failed.";
      errorEl.hidden = false;
      submitBtn.disabled = false;
      submitBtn.textContent = "Sign in";
    }
  });

  signOutBtn.addEventListener("click", () => {
    clearToken();
    form.hidden = false;
    successEl.hidden = true;
    form.reset();
    submitBtn.disabled = false;
    submitBtn.textContent = "Sign in";
  });
})();
