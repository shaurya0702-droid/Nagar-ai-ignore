/* ═══════════════════════════════════════════════════════════════════════════
   NagarAI — Authentication Controller
   ═══════════════════════════════════════════════════════════════════════════ */

/** Redirect to login if no token present */
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    window.location.href = 'login.html';
  }
}

/** Handle login form submission */
async function handleLogin(event) {
  event.preventDefault();

  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const btn      = document.getElementById('login-btn');
  const errEl    = document.getElementById('login-error');

  // Clear previous error
  errEl.textContent = '';
  errEl.classList.remove('visible');

  // Loading state
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner">⟳</span> Authenticating…';

  try {
    const result = await API.login(email, password);

    if (result.success) {
      // Brief success flash then redirect
      btn.innerHTML = '✅ Authenticated';
      btn.style.background = 'var(--green-low)';
      setTimeout(() => { window.location.href = 'dashboard.html'; }, 600);
    } else {
      throw new Error(result.error || 'Invalid credentials');
    }
  } catch (err) {
    errEl.textContent = err.message || 'Authentication failed. Please try again.';
    errEl.classList.add('visible');
    btn.disabled = false;
    btn.innerHTML = '🔐 Authenticate';
  }
}

/** Populate officer info in dashboard sidebar */
function displayOfficerInfo() {
  const officer = Auth.getOfficer();
  if (!officer) return;

  const nameEl = document.getElementById('officer-name');
  const roleEl = document.getElementById('officer-role');
  const wardEl = document.getElementById('officer-ward');

  if (nameEl) nameEl.textContent = officer.name || 'Officer';
  if (roleEl) roleEl.textContent  = (officer.role || 'officer').toUpperCase();
  if (wardEl) wardEl.textContent  = officer.ward_id ? `Ward ${officer.ward_id}` : 'All Wards';
}

/** Logout and redirect */
function logout() {
  Auth.clear();
  window.location.href = 'login.html';
}

/** Toggle password visibility */
function togglePassword() {
  const input = document.getElementById('login-password');
  const btn   = document.getElementById('toggle-pwd');
  if (input.type === 'password') {
    input.type = 'text';
    btn.textContent = '🙈';
  } else {
    input.type = 'password';
    btn.textContent = '👁️';
  }
}

/** Adjust font size for accessibility */
function adjustFont(factor) {
  const cur = parseFloat(getComputedStyle(document.documentElement).fontSize);
  document.documentElement.style.fontSize = (cur * factor) + 'px';
}

/** Mobile nav toggle */
function toggleMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  if (menu) menu.classList.toggle('open');
}

/* ── Auto-redirect if already logged in (login page) ─────────────────────── */
if (document.getElementById('login-email')) {
  if (Auth.isLoggedIn()) {
    window.location.href = 'dashboard.html';
  }
}
