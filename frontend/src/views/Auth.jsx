import React, { useState } from "react";
import { LockKeyhole, UserPlus } from "lucide-react";

const initialRegister = {
  username: "",
  email: "",
  password: "",
  full_name: "",
  organization: "",
  role: "program_manager"
};

export function AuthView({ loginUser, registerUser }) {
  const [mode, setMode] = useState("login");
  const [loginForm, setLoginForm] = useState({ username: "", password: "" });
  const [registerForm, setRegisterForm] = useState(initialRegister);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submitLogin(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await loginUser(loginForm);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function submitRegister(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await registerUser(registerForm);
      setMessage("Your application has been submitted. You will receive an email after admin review.");
      setRegisterForm(initialRegister);
      setMode("login");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="authShell">
      <section className="authPanel">
        <div className="brandBlock authBrand">
          <div className="brandMark">ES</div>
          <div>
            <h1>EcoSync AI</h1>
            <p>Secure ecosystem workspace</p>
          </div>
        </div>
        <div className="authTabs">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Register</button>
        </div>
        {error && <div className="alert">{error}</div>}
        {message && <div className="notice">{message}</div>}
        {mode === "login" ? (
          <form className="authForm" onSubmit={submitLogin}>
            <label>Username<input required value={loginForm.username} onChange={(event) => setLoginForm({ ...loginForm, username: event.target.value })} /></label>
            <label>Password<input required type="password" value={loginForm.password} onChange={(event) => setLoginForm({ ...loginForm, password: event.target.value })} /></label>
            <button className="primaryButton" disabled={busy}><LockKeyhole size={18} />{busy ? "Checking..." : "Login"}</button>
          </form>
        ) : (
          <form className="authForm" onSubmit={submitRegister}>
            <label>Username<input required value={registerForm.username} onChange={(event) => setRegisterForm({ ...registerForm, username: event.target.value })} /></label>
            <label>Email<input required type="email" value={registerForm.email} onChange={(event) => setRegisterForm({ ...registerForm, email: event.target.value })} /></label>
            <label>Password<input required type="password" value={registerForm.password} onChange={(event) => setRegisterForm({ ...registerForm, password: event.target.value })} /></label>
            <label>Full name<input required value={registerForm.full_name} onChange={(event) => setRegisterForm({ ...registerForm, full_name: event.target.value })} /></label>
            <label>Organization<input required value={registerForm.organization} onChange={(event) => setRegisterForm({ ...registerForm, organization: event.target.value })} /></label>
            <label>Role<select required value={registerForm.role} onChange={(event) => setRegisterForm({ ...registerForm, role: event.target.value })}>
              <option value="program_manager">Program manager</option>
              <option value="ecosystem_partner">Ecosystem partner</option>
              <option value="admin_operator">Admin operator</option>
            </select></label>
            <button className="primaryButton" disabled={busy}><UserPlus size={18} />{busy ? "Submitting..." : "Submit application"}</button>
          </form>
        )}
      </section>
    </main>
  );
}
